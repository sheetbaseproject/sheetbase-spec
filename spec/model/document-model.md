---
type: Component Design
title: Document model
description: "The in-memory document: tables, typed columns, the columnar row store, stable ids, and the metadata tables as typed records, with the Rust types sheetbase-core exposes."
tags: [model, core, rust]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-schema
    resource: https://github.com/gristlabs/grist-core/blob/main/sandbox/grist/schema.py
    title: schema.py (SCHEMA_VERSION = 47, every _grist_* table)
---

# Identity

```rust
pub type RowId = i64;                                  // > 0 for real rows; 0 is the empty record
#[derive(Copy, Clone, Eq, PartialEq, Hash, Ord, PartialOrd)] pub struct TableId(pub u32);   // index into Document.tables, stable for the session
#[derive(Copy, Clone, Eq, PartialEq, Hash, Ord, PartialOrd)] pub struct ColumnId(pub u32);  // index into Table.columns, stable for the session
pub type TableName = SmolStr;                          // Grist tableId, e.g. "Orders"
pub type ColumnName = SmolStr;                         // Grist colId, e.g. "Amount"
```

`TableId`/`ColumnId` are session-stable dense handles; names are what formulas and files use.
Renames change the name, not the handle. The metadata `_grist_Tables.id` and
`_grist_Tables_column.id` row ids (`colRef`, `tableRef` in Grist) are kept alongside because
fields, filters, rules and ACL resources refer to them.

# Document

```rust
pub struct Document {
    pub info: DocInfo,                         // _grist_DocInfo row 1: schemaVersion, timezone, documentSettings
    pub tables: IndexMap<TableName, Table>,    // user tables AND _grist_* metadata tables, uniform
    pub meta: MetaIndex,                       // typed views over the _grist_* tables (below)
    pub graph: GraphHandle,                    // sheetbase-graph::Graph instance + node registry
    pub history: ActionHistory,                // in-memory tail of _sheetbase_ActionHistory
    pub formulas: FormulaRegistry,             // compiled programs per formula column, dialect flags
    pub acl: RuleSet,                          // compiled access rules
    pub user: User,                            // the process user (ADR-013)
}

pub struct Table {
    pub id: TableId,
    pub meta_ref: RowId,                        // _grist_Tables.id
    pub name: TableName,
    pub columns: IndexMap<ColumnName, Column>,  // in parentPos order; "id" and "manualSort" first
    pub store: ColumnStore,
    pub summary_source: Option<TableId>,        // _grist_Tables.summarySourceTable
    pub locked: bool,
    pub on_demand: bool,                        // preserved, ignored
}

pub struct Column {
    pub id: ColumnId,
    pub meta_ref: RowId,                        // _grist_Tables_column.id (colRef)
    pub name: ColumnName,
    pub label: SmolStr,
    pub ty: ColumnType,
    pub kind: ColumnKind,                       // Data | Formula | Trigger | Empty (isFormula && formula == "")
    pub formula: Option<FormulaRef>,            // handle into FormulaRegistry
    pub recalc_when: RecalcWhen,                // Default = 0, Never = 1, ManualUpdates = 2
    pub recalc_deps: Vec<ColumnId>,
    pub widget_options: WidgetOptions,          // parsed JSON, unknown keys preserved
    pub visible_col: Option<ColumnId>,          // target-table column shown for Ref/RefList
    pub display_col: Option<ColumnId>,          // the gristHelper_Display column
    pub rules: Vec<ColumnId>,                   // gristHelper_ConditionalRule columns
    pub reverse_col: Option<ColumnId>,          // two-way reference partner
    pub summary_source_col: Option<ColumnId>,
    pub description: SmolStr,
    pub untie_col_id_from_label: bool,
}

#[derive(Clone, PartialEq, Eq, Hash)]
pub enum ColumnType {
    Any, Attachments, Blob, Bool, Choice, ChoiceList, Date,
    DateTime(TzId), Id, Int, ManualSortPos, Numeric, PositionNumber,
    Ref(TableName), RefList(TableName), Text,
}
impl ColumnType {
    pub fn parse(s: &str) -> Result<Self, TypeParseError>;   // "DateTime:America/New_York", "Ref:Orders"
    pub fn to_grist(&self) -> SmolStr;
    pub fn default_value(&self) -> Value;                     // Grist _type_defaults
    pub fn accepts(&self, v: &Value) -> bool;                 // Grist is_right_type
    pub fn sql_affinity(&self) -> SqlAffinity;                // Text | Integer | Numeric | Blob | Boolean | Date | DateTime
}

pub enum ColumnKind { Data, Formula, Trigger, Empty }
```

# ColumnStore

The store is columnar and typed; `Value` is materialised on read.

```rust
pub struct ColumnStore {
    pub row_ids: RowIndex,                      // RowId -> dense slot, slot -> RowId; live rows bitmap
    pub columns: Vec<ColumnData>,               // indexed by ColumnId.0
    pub deltas: DeltaLog,                       // per column: Vec<(NodeVersion, RowSet)>, bounded (see recalc)
}

pub enum ColumnData {
    Bool { bits: BitVec, null: BitVec },
    Int(Vec<i64>),                              // Int, Id, Ref (0 = none)
    Num(Vec<f64>),                              // Numeric, Date, PositionNumber, ManualSortPos; NaN never stored, null bitmap instead
    DateTime { secs: Vec<f64>, tz: TzId, null: BitVec },
    Text(Vec<SmolStr>),                         // Text, Choice
    TextList { offsets: Vec<u32>, items: Vec<SmolStr>, null: BitVec },   // ChoiceList
    IdList   { offsets: Vec<u32>, items: Vec<i64>,     null: BitVec },   // RefList, Attachments
    Any(Vec<Value>),                            // Any, Blob, and every column's AltText fallback below
}

pub struct TypedColumn {
    pub data: ColumnData,
    pub alt: Option<HashMap<u32, Value>>,       // slot -> raw wrong-type value (AltText), sparse
    pub errors: Option<HashMap<u32, Arc<CellError>>>, // slot -> formula error, sparse
}

impl ColumnStore {
    pub fn get(&self, col: ColumnId, row: RowId) -> Value;             // materialises; AltText/error aware
    pub fn set(&mut self, col: ColumnId, row: RowId, v: Value) -> Result<Prev, StoreTypeError>; // records delta
    pub fn add_rows(&mut self, ids: &[RowId]);                         // allocates slots, defaults every column
    pub fn remove_rows(&mut self, ids: &[RowId]) -> RemovedRows;       // returns non-default values for the inverse action
    pub fn live(&self) -> &RowSet;
}
```

Memory for a 1M-cell table (100k rows x 10 columns, 6 Numeric, 2 Text, 1 Ref, 1 Bool): 6 x 800
KB + 2 x (100k x 24 B) + 800 KB + 25 KB = about 11 MB, plus one `RowSet` per delta entry.

# Metadata as typed records

Every `_grist_*` table is an ordinary `Table` in `Document.tables` (so `AddRecord` on
`_grist_Views_section` goes through the same path), and `MetaIndex` holds typed, lazily rebuilt
views:

```rust
pub struct MetaIndex {
    pub tables: BTreeMap<RowId, TableRec>,           // _grist_Tables
    pub columns: BTreeMap<RowId, ColumnRec>,         // _grist_Tables_column
    pub views: BTreeMap<RowId, ViewRec>,             // _grist_Views
    pub sections: BTreeMap<RowId, SectionRec>,       // _grist_Views_section
    pub fields: BTreeMap<RowId, FieldRec>,           // _grist_Views_section_field
    pub pages: Vec<PageRec>,                         // _grist_Pages in pagePos order, tree from indentation
    pub tab_bar: Vec<RowId>,                         // _grist_TabBar
    pub filters: BTreeMap<RowId, FilterRec>,         // _grist_Filters
    pub acl_resources: BTreeMap<RowId, AclResourceRec>,
    pub acl_rules: Vec<AclRuleRec>,                  // rulePos order
    pub attachments: BTreeMap<RowId, AttachmentRec>,
    pub cells: BTreeMap<RowId, CellRec>,             // _grist_Cells (comments), read-only in v1
    pub triggers: Vec<TriggerRec>,                   // _grist_Triggers, preserved, not executed
    pub shares: Vec<ShareRec>,
    pub validations: Vec<ValidationRec>,             // legacy, preserved
}
```

The complete column list of each metadata table is Grist's schema v47,[^grist-schema] copied
into [storage](storage-sqlite.md) as DDL. Deprecated tables (`_grist_Imports`,
`_grist_External_database`, `_grist_External_table`, `_grist_TableViews`, `_grist_TabItems`,
`_grist_ACLPrincipals`, `_grist_ACLMemberships`, `_grist_REPL_Hist`) are preserved as plain tables
with no typed view.

# Schema consistency

As Grist's `assert_schema_consistent()`, after every bundle that touched a schema action the
engine rebuilds `Schema` from `_grist_Tables` + `_grist_Tables_column` and diffs it against
`Document.tables`; a mismatch is `ActionError::SchemaInconsistent { table, column, detail }` and
rolls the bundle back. This runs in debug builds and in `sb check`; in release builds it runs
once per save.

[^grist-schema]: schema.py (SCHEMA_VERSION = 47, every _grist_* table)
