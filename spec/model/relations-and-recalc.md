---
type: Component Design
title: Relations and recalc
description: "The formula-column compute in detail: dirty sets and the DeltaLog, relation types and affected-row mapping, the staging overlay and rollback, trigger formulas, the cycle-group evaluator, and error cells."
tags: [model, engine, recalc]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-engine
    resource: https://github.com/gristlabs/grist-core/blob/main/sandbox/grist/engine.py
    title: engine.py (_recompute_step, OrderError, _locked_cells, _prevent_recompute_map, _changes_map)
---

# Dirty sets

```rust
pub struct DeltaLog { per_column: Vec<VecDeque<(u64 /*version*/, RowSet)>>, cap: usize /* 64 entries per column */ }
pub enum RowSet { All, Some(RoaringBitmap) }   // roaring 0.10, MIT OR Apache-2.0

impl DeltaLog {
    pub fn record(&mut self, col: ColumnId, version: u64, rows: RowSet);
    /// Union of every entry with version > since. If `since` is older than the oldest kept
    /// entry, returns All (the dependent recomputes everything, which is always correct).
    pub fn since(&self, col: ColumnId, since: u64) -> RowSet;
}
```

A compute asks `host.deltas(node, version_seen)` for each dependency; the facade stores
`version_seen` per `(derived, dep)` pair after each successful run.

# Relations

Signatures from [ADR-005](../decisions/adr-005-relations-on-causl.md). How each kind maps rows:

| Relation | `affected_rows(changed_in_U)` | Maintained from |
|---|---|---|
| `Identity` | `changed` | nothing |
| `SingleRowsIdentity` | `changed` unless `All`, then empty | nothing (trigger `recalcDeps`) |
| `Reference { ref_col }` | union over `u in changed` of `inverse[u]` | the Ref column's data: `RefInverse` is `HashMap<RowId, RowSet>` rebuilt incrementally from the Ref column's own deltas |
| `Lookup { index, keys }` | rows of D whose key tuple is in the set of keys whose row set changed (the index compute reports changed keys as its delta) | the compute records `(row, keys)` per `lookupRecords` call |
| `SummaryGroup { helper }` | summary rows whose group membership changed (helper delta) | helper compute |
| `Composed(a, b)` | `a.affected_rows(b.affected_rows(changed))` | both |

The tracked reader builds relations: when the formula for row `r` reads `$Customer.Name`, the
`Record` for `Customer` carries `Relation::Reference { ref_col: Customer }`, and reading `.Name`
on it registers dependency `(model:Customers.Name, Reference{Customer})`. Reading `$Amount`
registers `(model:Orders.Amount, Identity)`. `Orders.lookupRecords(Customer=$id)` registers
`(model:Orders.#lookup#Customer, Lookup{...})` and records `(r, (id,))` in the relation's key map.

# The compute, concretely

```rust
pub struct FormulaCompute {
    pub col: ColumnId, pub table: TableId,
    pub program: Arc<Program>,                        // compiled SFL
    pub relations: HashMap<NodeRef, Relation>,
    pub full_recompute_pending: bool,                 // set by schema phase when the formula or a dep's schema changed
}

impl Compute for FormulaCompute {
    fn run(&mut self, reader: &mut dyn TrackedReader, host: &mut dyn ComputeHost) -> Result<Token, ComputeFailure> {
        let live = host.store().live_rows(self.table);
        let mut dirty = if self.full_recompute_pending { RowSet::All } else {
            let mut d = RowSet::empty();
            for (node, rel) in &self.relations {
                let changed = host.deltas(*node, reader.version_seen(*node).unwrap_or(0));
                d |= rel.affected_rows(&changed, host.store());
            }
            d
        };
        dirty &= live;
        let mut tracker = RelationTracker::new(self.table, &mut self.relations);
        tracker.reset_rows(&dirty);
        let mut changed_rows = RowSet::empty();
        for row in dirty.iter() {
            let out = evaluate(&self.program, row, &mut tracker, reader, host)?;   // Err only for engine bugs; formula errors are Values
            let out = host.store().column_type(self.col).convert(out);              // Grist col.convert(): wrong types become AltText, never panic
            if host.staging().write_if_changed(self.col, row, out) { changed_rows.insert(row); }
        }
        self.relations = tracker.finish();                                          // dynamic deps; reader already recorded the node reads
        self.full_recompute_pending = false;
        host.staging().record_delta(self.col, changed_rows);
        Ok(Token(reader.self_version() + 1))
    }
}
```

`write_if_changed` uses `Value::strict_eq` (Grist's `strict_equal`), so a recompute that
produces the same values records no delta and the token still bumps (Causl needs a changed value
to propagate the version; dependents then see an empty delta and do nothing: cheap).

Per-row budget: the interpreter targets 1 microsecond for `$A * $B`-class formulas and 5
microseconds for a lookup with one key. See [performance budgets](../quality/performance-budgets.md).

# Staging overlay and rollback

```rust
pub struct CommitStaging {
    writes: HashMap<ColumnId, HashMap<u32 /*slot*/, Value>>,  // sparse; merged on success
    deltas: Vec<(ColumnId, RowSet)>,
    errors: HashMap<ColumnId, HashMap<u32, Arc<CellError>>>,
}
```

Reads during a commit go through `ColumnStoreView`, which consults `writes` first. On
`GraphError` the overlay is dropped; the store is untouched. On success the overlay is merged
and the deltas appended to `DeltaLog`. gridcraft's COW-band idea was considered and rejected:
the overlay is sparser for typical commits (one cell changed) and the merge is O(writes).

# Trigger formulas

A `Trigger` column is a data (input) node. Its formula runs in the action pipeline's step 4,
not in a Causl compute: for rows selected by `recalcWhen` (`Default`: new rows and rows where a
`recalcDeps` column changed in this bundle; `ManualUpdates`: any row the user updated; `Never`:
only when the formula column itself is written with `['S']`-free values), evaluate with `value`
= current cell (`restore = true`), `user` = the bundle's user, write the result as a
`BulkUpdateRecord` with `direct = false`, which then bumps the input node like any data write.
Grist's `_prevent_recompute_map` becomes: a cell the user set explicitly in this bundle is
excluded from the trigger's row set. Errors keep `user_input`.

# Cycle groups

`CycleGroupCompute { members: Vec<ColumnId>, programs, relations }` implements Grist's
`_recompute_step` with `OrderError`:[^grist-engine] a `VecDeque<(ColumnId, RowId)>` work list,
a `HashSet<(ColumnId, RowId)>` of locked cells, and a reader whose `read_cell(col, row)` for a
member column either returns the staged value, or (if not computed this pass) pushes the current
cell back, pushes the needed cell with a lock, and returns `Suspend`. A read of a locked cell
yields `CircularRefError` stored in the requesting cell. Progress is guaranteed by the same
counter Grist uses (`ComputeFailure::NoProgress` after `members.len() * rows * 2` steps without
a completed cell).

# Error cells

A formula that raises produces `Value::Error(CellError { kind, message, details: None,
user_input })`. `details` (the traceback-like expansion: the SFL call stack with source spans) is
computed on demand by `sb explain`/the UI tooltip through `Engine::formula_error(table, col,
row) -> CellError` which re-evaluates that one cell with tracing on, as Grist's
`get_formula_error` does. Side effects of a failed evaluation (none exist in SFL: there is no
`lookupOrAddDerived` in v1 formulas; summary row creation lives in the helper compute) need no
checkpointing.

Reading an error cell from another formula raises `CellError` with the message suffixed
`"\n(in referenced cell {T}[{r}].{c})"`, matching Grist's `CellError` wrapping; `CircularRefError`
is re-raised unwrapped.

[^grist-engine]: engine.py (_recompute_step, OrderError, _locked_cells, _prevent_recompute_map, _changes_map)
