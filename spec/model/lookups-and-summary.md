---
type: Component Design
title: Lookups and summary tables
description: lookupRecords/lookupOne/CONTAINS/order_by as index nodes and relations; reference and reference-list columns with two-way references; summary tables as auto-maintained tables with a helper node, group column, auto-created rows and auto-removed empty groups.
tags: [model, engine, lookups, summary]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-lookup
    resource: https://github.com/gristlabs/grist-core/blob/main/sandbox/grist/lookup.py
    title: lookup.py (LookupMapColumn, SimpleLookupMapping, ContainsLookupMapping, SortedLookupMapColumn, make_sort_spec)
  - id: grist-summary
    resource: https://github.com/gristlabs/grist-core/blob/main/sandbox/grist/summary.py
    title: summary.py and summary_helper.py (encode_summary_table_name, group column, SummaryHelperColumn, auto-remove)
  - id: grist-colrefs-help
    resource: https://support.getgrist.com/col-refs/
    title: Grist help, references and lookups
---

# Lookup index nodes

`Table.lookupRecords(**kw)` in a formula resolves, at the call, to a `LookupIndex` node on the
*target* table keyed by the sorted tuple of column names with `CONTAINS` markers attached, as
Grist names them: `model:Orders.#lookup#Customer:Status`, and with a sort suffix for
`order_by`: `model:Orders.#lookup#Customer#Placed:-Amount`.[^grist-lookup]

```rust
pub struct LookupIndexCompute {
    pub table: TableId,
    pub key_cols: Vec<(ColumnId, KeyMode)>,       // KeyMode: Exact | Contains { match_empty: Option<Value> }
    pub map: TwoWayMap<RowId, KeyTuple>,          // row -> keys (Contains yields the product of list items), key -> rows
    pub changed_keys: Vec<KeyTuple>,              // delta reported for this run
}
impl Compute for LookupIndexCompute {
    fn run(&mut self, reader, host) -> Result<Token, ComputeFailure> {
        // deps: model:T.#rows and every key column (Identity relation)
        let dirty = rows changed in #rows or any key column since last seen;
        for row in dirty { self.map.remove_row(row); if live { self.map.insert(row, keys_of(row)) } ; record changed keys }
        host.staging().record_lookup_delta(self.node, &self.changed_keys);
        Ok(next token)
    }
}
```

`KeyTuple` is a `SmallVec<[KeyValue; 2]>` where `KeyValue` is `Value` normalised for equality
the Grist way (ints and floats compare numerically, `Ref` by id, strings exactly). Lookup by a
`Ref` column reuses the `RefInverse` map the `Reference` relation already maintains
(`ReferenceLookupMapping`), so `lookupRecords(Customer=$id)` costs no extra index.

A formula calling `lookupRecords` registers `(index node, Relation::Lookup { keys })`; the
dependent's `affected_rows` is "every D row whose recorded key is among `changed_keys`". Unused
index nodes are disposed at the end of a bundle when no relation references them (Grist's
`mark_lookupmap_for_cleanup`).

`lookupOne` = `lookupRecords(...).get_one()` (the first by `manualSort`, `id` tie-break, or the
`order_by`). `.all` = index with no key columns (`AllLookupMapping`). Sorted indexes keep a
`Vec<RowId>` per key sorted by the `order_by` spec with `manualSort` auto-appended unless `id` is
named, and support `find.lt/le/gt/ge/eq/previous/next` by bisection.[^grist-colrefs-help]
`Table._num_rows()` and `len(Table.all)` take the fast path with no key index.

# Reference columns

- `Ref:T` stores `i64` row ids; `RefList:T` stores id lists. Setting a Ref from the UI goes
  through `visibleCol`: the editor shows `displayCol` values (`gristHelper_Display` formula
  `$Customer.Name`), and committing a typed value sends `['l', value, {column}]`, which the
  engine resolves through the target column's lookup index to an id, or stores the text as
  AltText.
- `RefInverse` per Ref column is `HashMap<RowId, RoaringBitmap>` updated from the column's own
  deltas; it serves both the `Reference` relation and `lookupRecords(RefCol=...)`.
- Two-way references (`reverseCol`): `prepare_new_values` on a write to one side emits
  adjusting `BulkUpdateRecord`s on the partner (removing the old back-reference, adding the new
  one), `direct = false`, in the same bundle; a `Ref` partner that would need two values raises
  `ActionError::UniqueReferenceViolation { table, col, row }` and the bundle fails. Ported with
  `test_twoway_refs.py` (45 KB) as the golden suite.
- Removing a referenced row leaves dangling ids, as Grist does; the display shows the id with a
  warning style (`#Ref` in red in Grist).

# Summary tables

Naming and metadata follow Grist exactly:[^grist-summary] table name
`{Source}_summary_{col1}_{col2}` (sorted), `_grist_Tables.summarySourceTable`, group-by columns
are data columns with `summarySourceCol` and flattened types (`ChoiceList` to `Choice`,
`RefList:T` to `Ref:T`), the mandatory `group` column is `RefList:{Source}` with formula
`table.getSummarySourceGroup(rec)`, default `count = len($group)` and `SUM($group.{c})` for every
Int/Numeric source column.

Mechanics:

- `model:{Source}.#summary#{SummaryTable}` is a derived node (`SummaryHelperCompute`) depending
  on `#rows` and the group-by source columns. For each dirty source row it computes the group
  key, looks it up in `key_map: HashMap<KeyTuple, RowId>`, and if the group has no summary row it
  **emits an `AddRecord` on the summary table** into the bundle (an indirect doc action, `direct
  = false`) and assigns the id. Causl computes may not create nodes, but a summary row is data,
  not a node, so this is allowed; the facade records that the compute emitted doc actions and
  the pipeline runs steps 3 to 5 again for them (bounded loop, see
  [actions](actions-and-undo.md)). The helper's inverse map (group row to source rows) is what
  the `group` column's `SummaryGroup` relation reads.
- Empty groups: after the commit, `apply_auto_removes` removes summary rows whose `group` is
  empty, as Grist's `docmodel.setAutoRemove` does.
- `UpdateSummaryViewSection` re-points a section at a different summary table and remaps
  fields and `sortColRefs`; `DetachSummaryViewSection` turns the summary into a real table with
  `group = {Source}.lookupRecords(c=$c, CONTAINS($c2, match_empty=...))`.
- Grouping by a list column uses `SummaryHelperListColumn` semantics: one source row maps to
  several groups (`RefList` helper), covered by `test_summary_choicelist.py`.

Performance: a summary over 100k source rows with 1000 groups costs one helper pass (100k key
computations, about 20 ms) on first build and then only dirty rows; the `count`/`SUM` formulas
recompute only groups whose membership or source values changed, through the `SummaryGroup`
relation.

[^grist-lookup]: lookup.py (LookupMapColumn, SimpleLookupMapping, ContainsLookupMapping, SortedLookupMapColumn, make_sort_spec)
[^grist-summary]: summary.py and summary_helper.py (encode_summary_table_name, group column, SummaryHelperColumn, auto-remove)
[^grist-colrefs-help]: Grist help, references and lookups
