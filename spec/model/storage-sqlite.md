---
type: Component Design
title: Storage (SQLite)
description: "The on-disk layout: Grist's user tables and _grist_* metadata at schema version 47, the _gristsys_* system tables we read, and the _sheetbase_* tables we add; transactions, migrations, the load and save paths."
tags: [model, storage, sqlite, grist-compat]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-schema
    resource: https://github.com/gristlabs/grist-core/blob/main/sandbox/grist/schema.py
    title: schema.py (schema_create_actions, SCHEMA_VERSION 47)
  - id: grist-docstorage
    resource: https://github.com/gristlabs/grist-core/blob/main/app/server/lib/DocStorage.ts
    title: "DocStorage.ts (docStorageSchema: _gristsys_* tables, PRAGMA user_version)"
---

# Connection

`rusqlite 0.41` with `bundled` feature. `PRAGMA journal_mode = WAL; PRAGMA synchronous =
NORMAL; PRAGMA foreign_keys = OFF` (Grist uses none). One writer connection per open document;
`sb` opens read-only (`SQLITE_OPEN_READ_ONLY`) unless the subcommand writes. Every action
bundle is one `BEGIN IMMEDIATE ... COMMIT`.

# User tables (as Grist creates them)

```sql
CREATE TABLE "Orders" (
  id INTEGER PRIMARY KEY,
  "manualSort" NUMERIC DEFAULT 1e999,
  "Customer" INTEGER DEFAULT 0,
  "Amount" NUMERIC DEFAULT 0,
  "Placed" DATE DEFAULT NULL,
  "Tags" TEXT DEFAULT NULL,
  "Notes" TEXT DEFAULT ''
);
```

Formula columns are stored too (their last computed values), so a document opens without an
engine. Types per [value encoding](value-encoding.md).

# Metadata tables (schema version 47)[^grist-schema]

Created with the same DDL path from `schema_create_actions()`. The columns, verbatim:

```sql
CREATE TABLE _grist_DocInfo (id INTEGER PRIMARY KEY, docId TEXT DEFAULT '', peers TEXT DEFAULT '', basketId TEXT DEFAULT '', schemaVersion INTEGER DEFAULT 0, timezone TEXT DEFAULT '', documentSettings TEXT DEFAULT '');
CREATE TABLE _grist_Tables (id INTEGER PRIMARY KEY, tableId TEXT DEFAULT '', primaryViewId INTEGER DEFAULT 0, summarySourceTable INTEGER DEFAULT 0, onDemand BOOLEAN DEFAULT 0, locked BOOLEAN DEFAULT 0, rawViewSectionRef INTEGER DEFAULT 0, recordCardViewSectionRef INTEGER DEFAULT 0);
CREATE TABLE _grist_Tables_column (id INTEGER PRIMARY KEY, parentId INTEGER DEFAULT 0, parentPos NUMERIC DEFAULT 1e999, colId TEXT DEFAULT '', type TEXT DEFAULT '', widgetOptions TEXT DEFAULT '', isFormula BOOLEAN DEFAULT 0, formula TEXT DEFAULT '', label TEXT DEFAULT '', description TEXT DEFAULT '', untieColIdFromLabel BOOLEAN DEFAULT 0, summarySourceCol INTEGER DEFAULT 0, displayCol INTEGER DEFAULT 0, visibleCol INTEGER DEFAULT 0, rules TEXT DEFAULT NULL, reverseCol INTEGER DEFAULT 0, recalcWhen INTEGER DEFAULT 0, recalcDeps TEXT DEFAULT NULL);
CREATE TABLE _grist_Views (id INTEGER PRIMARY KEY, name TEXT DEFAULT '', type TEXT DEFAULT '', layoutSpec TEXT DEFAULT '');
CREATE TABLE _grist_Views_section (id INTEGER PRIMARY KEY, tableRef INTEGER DEFAULT 0, parentId INTEGER DEFAULT 0, parentKey TEXT DEFAULT '', title TEXT DEFAULT '', description TEXT DEFAULT '', defaultWidth INTEGER DEFAULT 100, borderWidth INTEGER DEFAULT 1, theme TEXT DEFAULT '', options TEXT DEFAULT '', chartType TEXT DEFAULT '', layoutSpec TEXT DEFAULT '', filterSpec TEXT DEFAULT '', sortColRefs TEXT DEFAULT '', linkSrcSectionRef INTEGER DEFAULT 0, linkSrcColRef INTEGER DEFAULT 0, linkTargetColRef INTEGER DEFAULT 0, embedId TEXT DEFAULT '', rules TEXT DEFAULT NULL, shareOptions TEXT DEFAULT '');
CREATE TABLE _grist_Views_section_field (id INTEGER PRIMARY KEY, parentId INTEGER DEFAULT 0, parentPos NUMERIC DEFAULT 1e999, colRef INTEGER DEFAULT 0, width INTEGER DEFAULT 0, widgetOptions TEXT DEFAULT '', displayCol INTEGER DEFAULT 0, visibleCol INTEGER DEFAULT 0, filter TEXT DEFAULT '', rules TEXT DEFAULT NULL);
CREATE TABLE _grist_Pages (id INTEGER PRIMARY KEY, viewRef INTEGER DEFAULT 0, indentation INTEGER DEFAULT 0, pagePos NUMERIC DEFAULT 1e999, shareRef INTEGER DEFAULT 0, options TEXT DEFAULT '');
CREATE TABLE _grist_TabBar (id INTEGER PRIMARY KEY, viewRef INTEGER DEFAULT 0, tabPos NUMERIC DEFAULT 1e999);
CREATE TABLE _grist_Filters (id INTEGER PRIMARY KEY, viewSectionRef INTEGER DEFAULT 0, colRef INTEGER DEFAULT 0, filter TEXT DEFAULT '', pinned BOOLEAN DEFAULT 0);
CREATE TABLE _grist_ACLResources (id INTEGER PRIMARY KEY, tableId TEXT DEFAULT '', colIds TEXT DEFAULT '');
CREATE TABLE _grist_ACLRules (id INTEGER PRIMARY KEY, resource INTEGER DEFAULT 0, permissions INTEGER DEFAULT 0, principals TEXT DEFAULT '', aclFormula TEXT DEFAULT '', aclColumn INTEGER DEFAULT 0, aclFormulaParsed TEXT DEFAULT '', permissionsText TEXT DEFAULT '', rulePos NUMERIC DEFAULT 1e999, userAttributes TEXT DEFAULT '', memo TEXT DEFAULT '');
CREATE TABLE _grist_Attachments (id INTEGER PRIMARY KEY, fileIdent TEXT DEFAULT '', fileName TEXT DEFAULT '', fileType TEXT DEFAULT '', fileSize INTEGER DEFAULT 0, fileExt TEXT DEFAULT '', imageHeight INTEGER DEFAULT 0, imageWidth INTEGER DEFAULT 0, timeDeleted DATETIME DEFAULT NULL, timeUploaded DATETIME DEFAULT NULL);
CREATE TABLE _grist_Triggers (id INTEGER PRIMARY KEY, tableRef INTEGER DEFAULT 0, eventTypes TEXT DEFAULT NULL, isReadyColRef INTEGER DEFAULT 0, actions TEXT DEFAULT '', label TEXT DEFAULT '', memo TEXT DEFAULT '', enabled BOOLEAN DEFAULT 0, watchedColRefList TEXT DEFAULT NULL, options TEXT DEFAULT '', condition TEXT DEFAULT '');
CREATE TABLE _grist_Cells (id INTEGER PRIMARY KEY, tableRef INTEGER DEFAULT 0, colRef INTEGER DEFAULT 0, rowId INTEGER DEFAULT 0, root BOOLEAN DEFAULT 0, parentId INTEGER DEFAULT 0, type INTEGER DEFAULT 0, content TEXT DEFAULT '', userRef TEXT DEFAULT '', timeCreated DATETIME DEFAULT NULL, timeUpdated DATETIME DEFAULT NULL, resolved BOOLEAN DEFAULT 0);
CREATE TABLE _grist_Shares (id INTEGER PRIMARY KEY, linkId TEXT DEFAULT '', options TEXT DEFAULT '', label TEXT DEFAULT '', description TEXT DEFAULT '');
CREATE TABLE _grist_Validations (id INTEGER PRIMARY KEY, formula TEXT DEFAULT '', name TEXT DEFAULT '', tableRef INTEGER DEFAULT 0);
CREATE TABLE _grist_REPL_Hist (id INTEGER PRIMARY KEY, code TEXT DEFAULT '', outputText TEXT DEFAULT '', errorText TEXT DEFAULT '');
-- deprecated but created for compatibility: _grist_Imports, _grist_External_database, _grist_External_table,
-- _grist_TableViews, _grist_TabItems, _grist_ACLPrincipals, _grist_ACLMemberships (columns as in schema.py)
```

Every metadata table also gets `manualSort` through the same `AddTable` path, as Grist does.

# System tables we read (and the ones we create empty)[^grist-docstorage]

```sql
CREATE TABLE _gristsys_Files (id INTEGER PRIMARY KEY, ident TEXT UNIQUE, data BLOB, storageId TEXT);
CREATE TABLE _gristsys_ActionHistory (id INTEGER PRIMARY KEY, actionHash TEXT UNIQUE, parentRef INTEGER, actionNum INTEGER, body BLOB);          -- read-only for us, marshal body
CREATE TABLE _gristsys_ActionHistoryBranch (id INTEGER PRIMARY KEY, name TEXT UNIQUE, actionRef INTEGER);
CREATE TABLE _gristsys_FileInfo (id INTEGER PRIMARY KEY CHECK (id = 0), docId TEXT, ownerInstanceId TEXT);
CREATE TABLE _gristsys_PluginData (id INTEGER PRIMARY KEY, pluginId TEXT, key TEXT, value BLOB, UNIQUE (pluginId, key));
-- legacy _gristsys_Action, _gristsys_Action_step are migrated away by Grist storage v3; if present we leave them.
```

`PRAGMA user_version` holds Grist's storage version (currently 3); we preserve it and never
write a value Grist does not know.

# sheetbase tables

```sql
CREATE TABLE _sheetbase_Meta (key TEXT PRIMARY KEY, value TEXT);            -- 'format' = '1', 'created_by' = 'sheetbase/<ver>', 'last_saved_by'
CREATE TABLE _sheetbase_Formulas (
  colRef INTEGER PRIMARY KEY,          -- _grist_Tables_column.id
  dialect TEXT NOT NULL,               -- 'sfl' | 'python' (imported, not compilable) | 'both' (compiles in SFL and is valid Python)
  status TEXT NOT NULL,                -- 'ok' | 'error' | 'unsupported'
  diagnostic TEXT,                     -- compile error text when status != 'ok'
  compiledHash TEXT                    -- blake3 of (formula text, dialect) to skip recompile on open
);
CREATE TABLE _sheetbase_ActionHistory (
  id INTEGER PRIMARY KEY,
  actionHash TEXT UNIQUE NOT NULL,     -- blake3 over canonical JSON of (actionNum, parentActionHash, info, stored)
  parentRef INTEGER,
  actionNum INTEGER NOT NULL,
  body TEXT NOT NULL                   -- JSON LocalActionBundle (see actions-and-undo)
);
CREATE TABLE _sheetbase_ActionHistoryBranch (name TEXT PRIMARY KEY, actionRef INTEGER);  -- 'shared', 'local_unsent' like Grist
CREATE TABLE _sheetbase_UiState (key TEXT PRIMARY KEY, value TEXT);          -- JSON: window, active page, cursor per section, panel widths
CREATE TABLE _sheetbase_Settings (key TEXT PRIMARY KEY, value TEXT);         -- document-level sheetbase settings
```

History is pruned like Grist's: keep at most 1000 bundles or 16 MiB of `body`, newest kept.

# Migrations

`sheetbase-store::migrations` ports `migrations.py` 1 through 47. Each is a function
`fn(&mut MigrationCtx) -> Vec<DocAction>` applied in a transaction with `schemaVersion` bumped in
`_grist_DocInfo`. Rule carried over: never remove or retype a metadata column, only add. Golden
tests: every `World-vN.grist`, `BlobMigrationVN.grist`, `DefaultValuesVN.grist`, `Pages-v19`,
`Memos-v34`, `Hooks-v37`, `Comments_44` fixture must open and, after migration, match the
shape of the current-version fixture of the same family.

# Load path

1. Open, check `PRAGMA user_version` and `_grist_DocInfo.schemaVersion`; migrate if below 47;
   refuse with `StoreError::SchemaTooNew { found, supported: 47 }` if above.
2. Read `_grist_Tables` and `_grist_Tables_column`; build `Document.tables` skeletons.
3. For each table: one `SELECT * FROM "T" ORDER BY id`, decode per column into `ColumnData`.
4. Build `MetaIndex`, compile formulas (or trust `compiledHash`), build the graph, register
   nodes, run a verification recompute only if `--recalc` or if any formula's hash changed.
5. Load the `_sheetbase_ActionHistory` tail (last 200 bundles) for undo.

Budget: a 10 MB document (100k rows x 10 columns) loads in under 400 ms on the reference
machine; a fixture under 20 ms. See [performance budgets](../quality/performance-budgets.md).

# Save path

Stored doc actions of a committed bundle are translated to SQL inside the same transaction as
the history insert:

| DocAction | SQL |
|---|---|
| `BulkAddRecord(T, ids, cols)` | `INSERT INTO "T" (id, c1, ...) VALUES (?, ?, ...)` batched 500 rows per statement |
| `BulkUpdateRecord` | `UPDATE "T" SET c1 = ?, ... WHERE id = ?` per row, prepared once |
| `BulkRemoveRecord` | `DELETE FROM "T" WHERE id IN (...)` chunks of 500 |
| `ReplaceTableData` | `DELETE FROM "T"` then insert |
| `AddColumn` | `ALTER TABLE "T" ADD COLUMN "c" <type> DEFAULT <default>` |
| `RemoveColumn` | `ALTER TABLE "T" DROP COLUMN "c"` (SQLite 3.35+, bundled) |
| `RenameColumn` | `ALTER TABLE "T" RENAME COLUMN "a" TO "b"` |
| `ModifyColumn` (type change) | create `"T_tmp"` with new DDL, `INSERT ... SELECT`, drop, rename (Grist does the same) |
| `AddTable` | `CREATE TABLE ...` |
| `RemoveTable` | `DROP TABLE` |
| `RenameTable` | `ALTER TABLE RENAME` |

Formula column values changed by the commit are written as `BulkUpdateRecord`s flagged
`direct = false` in the bundle (Grist's "calc flushed into stored" behaviour).

[^grist-schema]: schema.py (schema_create_actions, SCHEMA_VERSION 47)
[^grist-docstorage]: DocStorage.ts (docStorageSchema: _gristsys_* tables, PRAGMA user_version)
