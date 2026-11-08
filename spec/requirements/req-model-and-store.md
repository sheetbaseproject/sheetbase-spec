---
type: Requirement
title: "Requirements: document model and storage"
description: "REQ-MODEL and REQ-STORE: Grist schema 47 compatibility, columnar store, value encoding, migrations, history."
tags: [requirements, model, storage]
status: draft
requirement_id: REQ-MODEL/REQ-STORE
priority: must
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

| Id | Requirement | Priority | Verification |
|---|---|---|---|
| REQ-MODEL-01 | Every `_grist_*` table and column of schema version 47 is represented and preserved, including deprecated tables and unknown `widgetOptions`/`options` keys. | must | fixture round-trip (f) in [testing](../quality/testing.md) |
| REQ-MODEL-02 | Every Grist column type is supported with Grist's default value and `is_right_type` validity rule; wrong-type values are preserved as AltText. | must | `test_types.py` port; `TypeEncoding.grist`, `InvalidValues.grist` |
| REQ-MODEL-03 | The column store holds a 100k x 10 Numeric/Text table in under 15 MB and materialises any cell in O(1). | must | `sb bench memory` |
| REQ-MODEL-04 | Row ids are stable integers; `manualSort` positions use Grist's relabeling so inserts emit the minimal adjustment set. | must | `test_relabeling.py` port, relabel proptest |
| REQ-MODEL-05 | Schema consistency (`_grist_Tables*` versus in-memory tables) is checked after schema actions and on `sb check`. | must | proptest 7 |
| REQ-STORE-01 | A `.grist` file at schema 47 opens, and after any sequence of actions saves to a SQLite file whose user tables Grist 1.x opens and reads identically. | must | fixture round-trip (f); manual open in Grist for 10 fixtures at M1 |
| REQ-STORE-02 | Documents at schema versions 1 to 46 migrate on open with Grist's migration semantics. | must | `World-v*`, `BlobMigrationV*`, `DefaultValuesV*` fixtures |
| REQ-STORE-03 | Value encoding to SQLite follows Grist's affinity and marshal rules byte-for-byte for the values Grist marshals. | must | marshal golden tests over every fixture blob |
| REQ-STORE-04 | Action history is persisted as JSON `LocalActionBundle`s in `_sheetbase_ActionHistory` and pruned at 1000 bundles / 16 MiB; Grist's marshal history is readable. | must | `sb history` on fixtures with history; proptest 2 across restarts |
| REQ-STORE-05 | Save is one SQLite transaction per bundle; a crash mid-save leaves the previous state intact. | must | kill-during-save test with WAL |
| REQ-STORE-06 | A document above schema 47 opens read-only with a clear message. | should | unit test with a doctored `schemaVersion` |
