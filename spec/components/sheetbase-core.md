---
type: Component
title: sheetbase-core
description: L1 crate with the Document, ColumnStore, metadata index, user and doc actions, the engine (pipeline, computes, relations, lookups, summaries, cycle groups, trigger formulas), access rules and the view model.
tags: [component, crate, core, engine]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Purpose

The document engine, in memory, with no SQLite and no egui. Types in
[document model](../model/document-model.md), pipeline in [actions](../model/actions-and-undo.md),
computes in [relations and recalc](../model/relations-and-recalc.md).

# Public surface

```rust
pub struct Engine { /* Document + Graph + FormulaRegistry + RuleSet */ }
impl Engine {
    pub fn new(doc: Document, graph: Box<dyn Graph>) -> Result<Engine, EngineError>;
    pub fn apply_user_actions(&mut self, actions: Vec<UserAction>, user: &User, info: ActionInfo) -> Result<ActionBundle, ActionError>;
    pub fn fetch_table(&self, table: &TableName, user: &User, opts: FetchOptions) -> Result<TableData, ActionError>;
    pub fn document(&self) -> &Document;
    pub fn view(&self) -> &ViewStore;
    pub fn set_controller(&mut self, writes: &[(ControllerNode, serde_json::Value)]) -> Result<CommitOutcome, GraphError>;
    pub fn formula_error(&self, table: &TableName, col: &ColumnName, row: RowId) -> Option<CellError>;
    pub fn explain_last_commit(&self) -> Option<Explain>;
    pub fn check(&self) -> CheckReport;                       // sb check semantics
}
pub mod actions { pub enum UserAction; pub enum DocAction; pub struct ActionBundle; pub struct ActionInfo; pub struct ActionSummary; }
pub mod model { pub struct Document; pub struct Table; pub struct Column; pub enum ColumnType; pub struct ColumnStore; pub struct MetaIndex; }
pub mod acl { pub struct User; pub struct RuleSet; pub struct Predicate; pub struct PermissionSet; }
pub mod view_model { pub struct ViewStore; pub struct SectionRec; pub struct FieldRec; pub struct LinkFilter; pub enum SortSpec; pub enum FilterSpec; }
pub mod wire { impl Value { to_grist, from_grist } pub struct TableData; }
```

# Modules

`model`, `meta`, `store`, `actions::{doc,user,apply,bundle,summary,hooks}`, `engine::{pipeline,
compute,relation,lookup,summary,cycle_group,trigger,relabel,intervals,staging}`, `acl::{parse,
eval,enforce}`, `view_model::{sort,filter,linking,rows,styles,layout}`, `wire`, `error`.

# Dependencies

`sheetbase-formula`, `sheetbase-graph`, `roaring`, `indexmap`, `smol_str`, `serde`,
`serde_json`, `thiserror`, `tracing`, `blake3`. `#![forbid(unsafe_code)]`.

# Size

About 22k lines (Grist's engine Python is about 15k; Rust is wordier; plus the view model that
Grist keeps client-side).

# Requirements carried

REQ-MODEL-01 to 05, REQ-ACTION-01 to 04, REQ-ENGINE-01 to 06, REQ-ACL-01 to 03, REQ-VIEW-01 to 03.
