---
type: Decision
title: "ADR-008: SQLite with the Grist schema, JSON action history, a marshal codec for compatibility"
description: Documents are SQLite files with Grist's exact user-table and _grist_* layout and value encoding so Grist can open what we save; sheetbase-only state lives in _sheetbase_* tables; action history is stored as JSON in our table and the Python-marshal history is read but never written.
tags: [decision, storage, sqlite]
status: draft
decision_id: ADR-008
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-docstorage
    resource: https://github.com/gristlabs/grist-core/blob/main/app/server/lib/DocStorage.ts
    title: DocStorage.ts (_getSqlType, _encodeValue, _decodeValue, docStorageSchema)
  - id: grist-actionhistory
    resource: https://github.com/gristlabs/grist-core/blob/main/app/server/lib/ActionHistoryImpl.ts
    title: ActionHistoryImpl.ts (_gristsys_ActionHistory body is Python marshal v2)
---

# Context

A `.grist` file is SQLite: one table per user table (`id INTEGER PRIMARY KEY`, `manualSort
NUMERIC DEFAULT 1e999`, typed columns with affinities per `_getSqlType`), the `_grist_*` metadata
tables created through the same DocActions, and `_gristsys_*` system tables (files, action
history as Python marshal blobs, plugin data).[^grist-docstorage][^grist-actionhistory] Cell
values are encoded with rules that dodge SQLite's type coercion: list types as JSON text, odd
values as marshal blobs, booleans only bare in `BOOLEAN` columns.

# Decision

- **Store = SQLite through `rusqlite` 0.41 (bundled SQLite, `MIT`)**, WAL mode, one connection
  per open document, all writes in one transaction per action bundle.
- **Layout = Grist's**, exactly. Same DDL, same affinities, same defaults, same `_encodeValue`
  and `_decodeValue` rules, including marshal v2 blobs for the cases Grist marshals. We implement
  `sheetbase-store::marshal` (encode and decode for `None`, `bool`, `int` incl. long, `float`,
  `str`/`unicode`, `bytes`, `list`, `tuple`, `dict`, about 300 lines) so a document we save is
  byte-compatible in its data tables with what Grist writes.
- **`_grist_DocInfo.schemaVersion = 47`** is what we read and write. Documents below 47 are
  migrated on open by a port of `migrations.py` for versions 1 to 47 (the fixtures include
  `World-v0` through `World-v39` and `BlobMigrationV1`..`V17`, so every step is golden-tested).
  Documents above 47 open read-only with a warning.
- **sheetbase-only state** lives in tables prefixed `_sheetbase_`, which Grist ignores:
  `_sheetbase_Formulas(colRef, dialect, status, compiledHash)`, `_sheetbase_ActionHistory(id,
  actionHash, parentRef, actionNum, body JSON)`, `_sheetbase_ActionHistoryBranch(name, actionRef)`,
  `_sheetbase_Settings(key, value)`, `_sheetbase_UiState(key, value)` (window geometry, last page,
  cursor per section). Full DDL in [storage](../model/storage-sqlite.md).
- **Action history**: we read `_gristsys_ActionHistory` (marshal) for display and for replaying a
  document's past, we never write it. Our own history is JSON (serde) in `_sheetbase_ActionHistory`
  with the same `LocalActionBundle` shape, so a future server can ship it to Grist's format if
  needed. Undo and redo use our table.
- **File extension**: `.sheetbase` by default. "Save as .grist" is offered when
  `_sheetbase_Formulas` has no `dialect = 'sfl-only'` rows (every formula is valid Python) and no
  `_sheetbase_*` state is load-bearing; otherwise the dialog explains what would be lost.
- **Attachments**: `_gristsys_Files` as Grist; `storageId` non-null (external store) is read as
  "missing attachment" in v1.

# Alternatives

**Our own schema with an import/export to .grist.** Cleaner tables (no marshal, no affinity
games). Lost: every Grist user has documents, and round-tripping through a converter loses the
guarantee that opening in Grist later works. Compatibility is the product's reason to exist.

**Keep Python-marshal action history for full compatibility.** We can write marshal; the codec
exists. Lost because Grist's history body includes `undo` doc actions computed by *its* engine
and `actionHash` over marshal bytes; our hashes would never match theirs, so "compatible" would
be an illusion. Reading it suffices.

**Columnar store on disk (Parquet, Arrow IPC).** Faster bulk load, no compatibility. Rejected
for v1; the in-memory `ColumnStore` is columnar, the disk is SQLite.

# Consequences

- Load path: SQLite rows into `ColumnStore` column by column (one `SELECT` per table, decoded by
  declared type), about 10 MB/s decode on marshal-heavy columns, 100 MB/s on plain ones; a
  10k-row fixture loads in under 20 ms.
- Save path: the bundle's stored doc actions become SQL statements in one transaction after the
  Causl commit succeeds. Formula results are stored too (Grist does this since `calc` actions
  were retired), so a document opens without recomputation and `sb export` needs no engine.
- Marshal correctness is proptested against the fixture blobs (every blob in every fixture must
  decode and re-encode to the same bytes).

[^grist-docstorage]: DocStorage.ts (_getSqlType, _encodeValue, _decodeValue, docStorageSchema)
[^grist-actionhistory]: ActionHistoryImpl.ts (_gristsys_ActionHistory body is Python marshal v2)
