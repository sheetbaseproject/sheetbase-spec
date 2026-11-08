---
type: Component Design
title: Actions and undo
description: "The action pipeline: user actions (all 43 Grist ones minus the import transforms), their expansion into doc actions, inverse computation, bundles, and how one bundle becomes one Causl commit."
tags: [model, actions, undo]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-useractions
    resource: https://github.com/gristlabs/grist-core/blob/main/sandbox/grist/useractions.py
    title: useractions.py (43 @useraction methods, override_action hooks)
  - id: grist-docactions
    resource: https://github.com/gristlabs/grist-core/blob/main/sandbox/grist/docactions.py
    title: docactions.py (apply + inverse per DocAction)
  - id: grist-bundle
    resource: https://github.com/gristlabs/grist-core/blob/main/app/common/ActionBundle.ts
    title: ActionBundle.ts (ActionBundle, SandboxActionBundle, LocalActionBundle)
---

# Doc actions

```rust
#[derive(Clone, Serialize, Deserialize)]
#[serde(untagged)]   // serialised as Grist's positional arrays: ["BulkUpdateRecord", "T", [1,2], {"c": [..]}]
pub enum DocAction {
    AddRecord        { table: TableName, row: RowId, values: ColumnValues },
    BulkAddRecord    { table: TableName, rows: Vec<RowId>, values: BulkColumnValues },
    RemoveRecord     { table: TableName, row: RowId },
    BulkRemoveRecord { table: TableName, rows: Vec<RowId> },
    UpdateRecord     { table: TableName, row: RowId, values: ColumnValues },
    BulkUpdateRecord { table: TableName, rows: Vec<RowId>, values: BulkColumnValues },
    ReplaceTableData { table: TableName, rows: Vec<RowId>, values: BulkColumnValues },
    AddColumn        { table: TableName, col: ColumnName, info: ColInfo },
    RemoveColumn     { table: TableName, col: ColumnName },
    RenameColumn     { table: TableName, old: ColumnName, new: ColumnName },
    ModifyColumn     { table: TableName, col: ColumnName, info: PartialColInfo },
    AddTable         { table: TableName, columns: Vec<ColInfoWithId> },
    RemoveTable      { table: TableName },
    RenameTable      { old: TableName, new: TableName },
}
pub type ColumnValues = IndexMap<ColumnName, Value>;
pub type BulkColumnValues = IndexMap<ColumnName, Vec<Value>>;   // column-oriented, as Grist
pub struct ColInfo { pub ty: ColumnType, pub is_formula: bool, pub formula: SmolStr, pub reverse_col_id: Option<ColumnName> }
```

`DocAction::simplify()` turns an empty bulk action into `None`, a one-row bulk into its singular
form. `is_schema_action()` is true for the six `*Column`/`*Table` variants.

# Inverses (`docactions.py` rules)[^grist-docactions]

| Applied | Inverse pushed onto `undo` |
|---|---|
| `BulkAddRecord` | `BulkRemoveRecord` |
| `BulkRemoveRecord` | `BulkAddRecord` with only non-default values |
| `BulkUpdateRecord` | `BulkUpdateRecord` with previous raw values (trigger-formula cells flagged `prevent_recalc`) |
| `ReplaceTableData` | `ReplaceTableData` with the old data |
| `AddColumn` | `RemoveColumn` |
| `RemoveColumn` | `[BulkUpdateRecord(non-default values)] + AddColumn` (formula values recomputed, not restored) |
| `RenameColumn` | the opposite rename |
| `ModifyColumn` | `ModifyColumn` with the old values of the touched keys |
| `AddTable` | `RemoveTable` |
| `RemoveTable` | `BulkAddRecord(all data)` then `AddTable` (so undo order, reversed, recreates then fills) |
| `RenameTable` | the opposite rename |

# User actions

All of `useractions.py` except `GenImporterView` and the three import-transform actions
(`TransformAndFinishImport`, `MakeImportTransformColumns`, `FillTransformRuleColIds`, whose
UI is replaced by our import wizard) and `EvalCode` (the REPL).[^grist-useractions]

```rust
#[derive(Clone, Serialize, Deserialize)]
#[serde(untagged)]   // ["UpdateRecord", "T", 5, {"Amount": 3}]
pub enum UserAction {
    InitNewDoc, ApplyDocActions(Vec<DocAction>), ApplyUndoActions(Vec<DocAction>), Calculate, UpdateCurrentTime,
    RespondToRequests { responses: Value, cached_keys: Value },      // accepted, returns NotSupported in v1
    AddRecord { table, row: Option<RowId>, values }, BulkAddRecord { table, rows: Vec<Option<RowId>>, values },
    ReplaceTableData { table, rows, values }, UpdateRecord { table, row, values }, BulkUpdateRecord { table, rows, values },
    BulkAddOrUpdateRecord { table, require: BulkColumnValues, values: BulkColumnValues, options: AddOrUpdateOptions },
    AddOrUpdateRecord { table, require: ColumnValues, values: ColumnValues, options: AddOrUpdateOptions },
    RemoveRecord { table, row }, BulkRemoveRecord { table, rows },
    AddColumn { table, col, info: ColInfoJson }, AddHiddenColumn { .. }, AddVisibleColumn { .. },
    RemoveColumn { table, col }, RenameColumn { table, old, new },
    SetDisplayFormula { table, field_ref: Option<RowId>, col_ref: Option<RowId>, formula },
    RemoveStaleObjects, ModifyColumn { table, col, info: PartialColInfoJson },
    ConvertFromColumn { table, src, dst, ty, widget_options, visible_col_ref },
    CopyFromColumn { table, src, dst, widget_options }, MaybeCopyDisplayFormula { src_col_ref, dst_col_ref },
    RenameChoices { table, col, renames: IndexMap<SmolStr, SmolStr> },
    AddEmptyRule { table, field_ref, col_ref }, AddReverseColumn { table, col },
    AddEmptyTable { table: Option<TableName> }, AddTable { table, columns }, AddRawTable { table },
    RemoveTable { table }, RenameTable { old, new },
    DuplicateTable { existing, new, include_data: bool },
    CreateViewSection { table_ref, view_ref, section_type: SectionType, groupby_colrefs: Option<Vec<RowId>>, table_id: Option<TableName> },
    UpdateSummaryViewSection { section_ref, groupby_colrefs }, DetachSummaryViewSection { section_ref },
    AddView { table, view_type, name }, RemoveView { view_id },
    AddViewSection { title, section_type, view_row_id, table }, RemoveViewSection { section_id },
}
```

Expansion follows Grist exactly, including the metadata-as-source-of-truth pattern: the
`UserAction::RemoveColumn` does not emit `DocAction::RemoveColumn` directly; it removes the
`_grist_Tables_column` row, and the `override_action` hook on `BulkRemoveRecord` for that table
emits the schema doc action. The eighteen `override_action` hooks are implemented as
`trait MetaHook { fn before(&mut self, ctx, action) -> Vec<DocAction>; fn after(...) }` keyed by
`(DocActionKind, TableName)`. Rules carried over verbatim: temp (negative) row ids resolved via
the bundle's `new_rows_map`; `next_row_id` refuses more than 1,000,000 new rows per bundle;
`_ensure_column_accepts_data` converts an Empty column to Data on first write (guessing the type
with Grist's `guessColInfo` order: Int, Numeric, Date, DateTime, Bool, Ref by visible value, Text);
writing to a Formula column is `ActionError::FormulaColumnWrite`; raw-data and record-card
sections cannot be removed (`ActionError::ProtectedSection`); locked tables refuse data changes
(`ActionError::TableLocked`).

# Bundles

```rust
pub struct ActionBundle {
    pub action_num: u64,
    pub action_hash: Blake3Hex,
    pub parent_action_hash: Option<Blake3Hex>,
    pub info: ActionInfo,              // time (ms), user, inst, desc, otherId, linkId
    pub user_actions: Vec<UserAction>,
    pub stored: Vec<DocAction>,
    pub direct: Vec<bool>,             // per stored: true if caused by the user action, false if engine (formula flush, auto-remove)
    pub undo: Vec<DocAction>,
    pub undo_owner: Vec<Option<usize>>, // which stored action produced each undo entry
    pub ret_values: Vec<serde_json::Value>,
    pub summary: ActionSummary,        // Grist's ActionSummary shape, for the UI's history view
    pub row_count: usize,
}
```

Serialised to JSON in `_sheetbase_ActionHistory.body`; the same struct, with
`envelopes = [{recipients: ["#ALL"]}]` and `calc = []`, is what `sb serve` returns, so it is
byte-for-byte a Grist `LocalActionBundle` in JSON form.[^grist-bundle] `action_hash` is blake3
over the canonical JSON of `(action_num, parent_action_hash, info, stored)`, which is not
Grist's marshal-based hash; the two histories are separate ([ADR-008](../decisions/adr-008-storage.md)).

# Pipeline: one request to one commit

```rust
impl Engine {
    pub fn apply_user_actions(&mut self, actions: Vec<UserAction>, user: &User, info: ActionInfo)
        -> Result<ActionBundle, ActionError>;
}
```

1. **ACL pre-check** (`check_user_actions`), see [access rules](access-rules.md).
2. **Expand**: each `UserAction` runs its handler, which emits doc actions through
   `self.do_doc_action(action)`; the handler applies each doc action to `Document` immediately
   (schema change, store write into the **staging overlay**, metadata row), records it in `stored`
   with `direct = true`, computes and records its inverse, and checks ACL per doc action against
   before/after rows.
3. **Schema phase for the graph**: node creation/disposal for added/removed columns, formula
   recompilation, cycle-group recomputation ([ADR-006](../decisions/adr-006-cycle-groups.md)),
   relation resets. Causl nodes are created and disposed here, never inside computes.
4. **Trigger dependencies** (`_maybe_update_trigger_dependencies`) and invalidation marks:
   each written data column node is queued with its dirty row set; `recalcWhen` rules decide
   which trigger columns get queued.
5. **One Causl commit**: `graph.commit(intent, writes)` where `writes` is one `(node,
   token(version+1))` per written input node. Causl drains every affected derived; each compute
   writes formula results into the staging overlay and records dirty rows.
6. **Auto-removes** (`docmodel.apply_auto_removes`): summary rows with empty groups, unused
   display and rule helper columns. These emit further doc actions and, if any, loop to step 3
   (bounded to 8 iterations, then `ActionError::AutoRemoveLoop`).
7. **Flush**: formula value changes from the overlay become `BulkUpdateRecord`s with `direct =
   false` plus their inverses; the overlay is merged into the store; the SQL transaction writes
   the stored actions and the history row; `graph.subscribers` fire (UI); `Ok(bundle)`.

Any error at steps 1 to 6 drops the overlay, reverts schema changes from a snapshot of
`Document.tables`'s metadata (schema actions are rare and the snapshot is cheap), and rolls the
graph back to its pre-step-3 node registry. Causl itself rolls back a rejected commit
byte-identically, so there is nothing to undo there.

# Undo and redo

`ApplyUndoActions(undo)` applies the list in reverse through steps 1 to 7. The client (UI or
`sb undo`) keeps the stack: `otherId` of an undo bundle is the `action_num` it reverses, and redo
re-sends the original bundle's `stored` list as `ApplyDocActions` with `otherId` pointing at the
undo. `linkId` chains bundles the UI considers one gesture (a paste that adds rows and updates
cells), so one Ctrl+Z reverses the chain.

[^grist-useractions]: useractions.py (43 @useraction methods, override_action hooks)
[^grist-docactions]: docactions.py (apply + inverse per DocAction)
[^grist-bundle]: ActionBundle.ts (ActionBundle, SandboxActionBundle, LocalActionBundle)
