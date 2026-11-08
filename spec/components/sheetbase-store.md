---
type: Component
title: sheetbase-store
description: "L2 crate for SQLite persistence: open and save with the Grist layout, value codec with marshal, migrations 1 to 47, action history, the _sheetbase_* tables."
tags: [component, crate, storage, sqlite]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Public surface

```rust
pub struct Store { conn: rusqlite::Connection, path: PathBuf, read_only: bool }
impl Store {
    pub fn open(path: &Path, opts: OpenOptions) -> Result<(Store, Document, MigrationReport), StoreError>;
    pub fn create(path: &Path) -> Result<(Store, Document), StoreError>;        // InitNewDoc applied
    pub fn save_bundle(&mut self, doc: &Document, bundle: &ActionBundle) -> Result<(), StoreError>;   // one transaction
    pub fn save_as(&self, doc: &Document, path: &Path, format: FileFormat) -> Result<(), StoreError>;  // .sheetbase | .grist (checks convertibility)
    pub fn history(&self) -> HistoryReader;
    pub fn ui_state(&self) -> UiStateTable;
    pub fn attachment(&self, ident: &str) -> Result<Option<Vec<u8>>, StoreError>;
}
pub mod codec { pub fn encode(v: &Value, aff: SqlAffinity) -> SqlParam; pub fn decode(v: SqlValue, ty: &ColumnType) -> Value; }
pub mod marshal { pub fn loads(b: &[u8]) -> Result<MarshalValue, MarshalError>; pub fn dumps(v: &MarshalValue) -> Vec<u8>; }
pub mod schema { pub const SCHEMA_VERSION: i64 = 47; pub fn ddl_for(table: &Table) -> String; }
pub mod migrations { pub fn migrate(doc: &mut Document, from: i64) -> Result<Vec<DocAction>, StoreError>; }
```

# Dependencies

`rusqlite 0.41` (`bundled`, `blob`, `functions` off), `sheetbase-core`, `sheetbase-formula`,
`serde_json`, `blake3`, `thiserror`. `#![forbid(unsafe_code)]` (rusqlite's unsafe is its own).

# Size

About 6k lines: DDL and codec 1200, marshal 400, migrations 2500 (47 steps), history 400,
load/save 1200, tests separately.

# Requirements carried

REQ-STORE-01 to 05.
