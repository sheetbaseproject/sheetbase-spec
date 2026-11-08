---
type: Decision
title: "ADR-005: Grist relations are layered on Causl, not replaced by it"
description: Causl owns the column-level graph (edges, order, glitch-freedom, cycles); sheetbase-core owns row-level relations (identity, reference, lookup, summary group) that run inside the compute to turn upstream dirty rows into the rows to recompute.
tags: [decision, causl, engine]
status: draft
decision_id: ADR-005
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-depend
    resource: https://github.com/gristlabs/grist-core/blob/main/sandbox/grist/depend.py
    title: depend.py (Node, Edge, Graph.invalidate_deps)
  - id: grist-relation
    resource: https://github.com/gristlabs/grist-core/blob/main/sandbox/grist/relation.py
    title: relation.py (IdentityRelation, SingleRowsIdentityRelation, ReferenceRelation, ComposedRelation)
  - id: grist-lookup
    resource: https://github.com/gristlabs/grist-core/blob/main/sandbox/grist/lookup.py
    title: lookup.py (LookupMapColumn, _LookupRelation, TwoWayMap)
---

# Context

Grist's `depend.py` has nodes `(table_id, col_id)` and edges carrying a `Relation` whose
`get_affected_rows(input_rows)` maps changed rows of the dependency to rows of the dependent to
recompute.[^grist-depend][^grist-relation] Lookups add `_LookupRelation` keyed by a `TwoWayMap`
of referring row to key tuples.[^grist-lookup] Causl has edges but no relations: an edge is a
whole-node dependency, and a commit tells a derived "something upstream changed", not which rows.

# Decision

Two layers with a clean seam:

**Causl layer (through `sheetbase-graph`)**: which column depends on which, discovered by
tracked reads during the compute and returned as the dep set; the topological order of
recomputation; the glitch-freedom guarantee (a derived column's compute runs once per commit,
after every dependency settled); cycle detection (`CycleClosed`); subscriptions for the UI.

**Relation layer (`sheetbase-core::engine::relation`)**: for each edge `(dependent column D,
dependency column U)` the compute keeps a `Relation` object:

```rust
pub enum Relation {
    /// Same row ids: `$Amount` read from the record's own table.
    Identity,
    /// Same row ids, but ALL_ROWS invalidation does not propagate (trigger-formula recalcDeps).
    SingleRowsIdentity,
    /// D rows reached U rows through a Ref column of D's table: `$Customer.Name`.
    /// Inverse map U row -> set of D rows, maintained from the Ref column's data.
    Reference { ref_col: ColumnId, inverse: RefInverse },
    /// `Table.lookupRecords(...)`: D row -> key tuples, index node tells key -> U rows.
    Lookup { index: NodeId, keys: TwoWayMap<RowId, KeyTuple> },
    /// Summary `group` column: summary row -> source rows via the helper column's inverse.
    SummaryGroup { helper: ColumnId },
    /// Composition `$a.b.c`: Reference(a) then Reference(b).
    Composed(Box<Relation>, Box<Relation>),
}

impl Relation {
    /// Rows of the dependent to recompute when `changed` rows of the dependency changed.
    pub fn affected_rows(&self, changed: &RowSet, store: &ColumnStore) -> RowSet;
    /// Forget everything recorded for these dependent rows (before they recompute).
    pub fn reset_rows(&mut self, rows: &RowSet);
}
```

The compute for a derived column `D` (pseudo-Rust, the real signatures are in
[relations and recalc](../model/relations-and-recalc.md)):

```
fn compute(D):
    dirty = RowSet::empty()
    for (U, rel) in D.relations:
        changed = store.delta_since(U, D.last_seen_version[U])   // rows of U changed since D last ran
        dirty |= rel.affected_rows(changed)
    if D.formula_changed or D.schema_changed: dirty = All
    dirty &= table(D).live_rows
    for rel in D.relations: rel.reset_rows(dirty)
    for row in dirty:
        value = evaluate(D.formula, row, tracked_reader)     // reader records (column, relation) reads
        staging.write(D, row, value)
    D.relations = tracked_reader.relations()                  // dynamic deps: stale edges dropped
    return token(D.version + 1), tracked_reader.nodes()
```

This is `_recompute_step` from `engine.py` with the per-node scheduling removed, because Causl
does the scheduling.

# Alternatives

**Replace relations with per-row nodes.** Rejected by [ADR-004](adr-004-column-granularity.md)'s
arithmetic.

**Give up row-level precision, recompute whole columns.** Simple, and Causl alone would suffice.
Rejected: a keystroke in a 100k-row table would cost 100 ms per dependent column, and Grist users
have those tables.

**Put relations into Causl as a new edge payload (fork Causl).** The brief wants Causl unmodified
and glitch-free semantics come from its pipeline; a fork would also break the mirror story.
Rejected; if upstream ever grows a "delta hint" on edges we can move `affected_rows` there.

# Consequences

- The `ALL_ROWS` special case in Grist (clearing dependencies on a full invalidation) becomes
  `dirty = All`, and the compute drops and rebuilds its relations, which is what Causl's
  "returned read set replaces deps" semantics want anyway.
- The `Node(table_id, None)` "new column" dependency of Grist (a formula referencing a missing
  column) becomes a dependency on the table's schema node `model:{Table}.#schema`, bumped by
  `AddColumn`/`RenameColumn`/`RemoveColumn`.
- `#now` becomes `model:#now`, an input bumped by `UpdateCurrentTime`.

[^grist-depend]: depend.py (Node, Edge, Graph.invalidate_deps)
[^grist-relation]: relation.py (IdentityRelation, SingleRowsIdentityRelation, ReferenceRelation, ComposedRelation)
[^grist-lookup]: lookup.py (LookupMapColumn, _LookupRelation, TwoWayMap)
