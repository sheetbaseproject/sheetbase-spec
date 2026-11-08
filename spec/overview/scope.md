---
type: Overview
title: Scope of v1
description: The feature set that v1 ships, stated as a checklist against Grist's feature list so nothing is implied.
tags: [overview, scope]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# In v1

Document model and storage
- Open, edit and save Grist documents at schema version 47 (every `_grist_*` table, every column
  type: `Any Attachments Blob Bool Choice ChoiceList Date DateTime[:tz] Id Int ManualSortPos Numeric PositionNumber Ref:T RefList:T Text`).
- Save as `.sheetbase` (same SQLite layout plus `_sheetbase_*` tables) or back to `.grist` when the
  document is Grist-compatible. See [storage](../model/storage-sqlite.md).
- Attachments stored in `_gristsys_Files`, shown as thumbnails, opened externally.

Engine
- Formula columns, trigger formulas (`recalcWhen`, `recalcDeps`), display columns
  (`gristHelper_Display`), conditional-format rule columns, lookups (`lookupRecords`, `lookupOne`,
  `CONTAINS`, sort `order_by`), summary tables (auto-created, auto-removed empty groups,
  detach), reference and reference-list columns with two-way references (`reverseCol`), manual
  sort positions with relabeling, locked tables.
- Every user action in Grist's `useractions.py` except the four import-transform ones (listed in
  [actions](../model/actions-and-undo.md)); undo and redo as inverse doc actions with the Grist
  bundle shape, so Grist can still replay our history where the formulas are compatible.
- Glitch-free recalculation through Causl: one commit per user action bundle, column-level
  nodes, row-level deltas through relations. See [Causl mapping](../model/causl-mapping.md).

Formula language
- The sheetbase formula language: a Python-expression subset with `$col`, `rec`, `table`,
  comprehensions, `if`/`else` expressions, small statement bodies, the Grist function library.
  Unsupported Python in an imported document is flagged, preserved verbatim and shown as a
  `#PYTHON` cell error until the user converts it. See [language](../formula/language.md) and
  [migration](../formula/migration.md).

Views
- Pages, grid (`record`), card (`single`), card list (`detail`), chart (`chart`: bar, line,
  area, scatter, pie, donut), raw data section, record card section. Linking: every
  `LinkingState` case Grist implements. Sort specs, saved and unsaved filters, pinned filters,
  frozen columns, row height options, column widths, card layouts (`layoutSpec`), conditional
  formatting on cells, columns and rows, choice colours, number and date formats.

Access rules
- The full rule grammar (`permissionsText`, `aclFormula` predicate), default rule set, user
  attribute tables, enforced in the action pipeline and in view filtering for a `User` the
  process is told about (`--as-user` in the CLI, the owner in the desktop app). See
  [access rules](../model/access-rules.md).

UI
- The grid port of xldatagrid (every component in the
  [traceability table](../references/xldatagrid-traceability.md) marked port or merge), card
  and card list, chart, page tree, creator panel (column, field, section and page settings),
  find, context menus, the keyboard model, clipboard with the Grist HTML flavour, drag reorder
  of rows and columns, column resize, freeze, theming in light and dark with measured contrast,
  HiDPI, 60 fps with virtualised rows and columns.

Import and export
- Import: `.grist` (open), `.csv`/`.tsv` (new table or into existing with column mapping),
  `.xlsx` (one table per sheet). Export: `.csv`/`.tsv` per section with sort and filter applied,
  `.xlsx` whole document, `.sheetbase`/`.grist` save.

Headless
- `sb` CLI: info, check, export, import, apply (JSON user actions), recalc, formula eval, migrate,
  bench, and `sb serve` (JSON-RPC 2.0 over stdio exposing the same user actions). See
  [CLI](../cli/surface.md).

# Explicitly deferred inside v1 features

- Custom widgets (`parentKey = 'custom'`) render as a placeholder card showing the widget URL;
  the section and its options are preserved untouched.
- Forms (`parentKey = 'form'`) likewise.
- Comments (`_grist_Cells`) are preserved and shown read-only.
- Attachments are not editable (no upload) in v1; they are displayed and preserved.
- `REQUEST()` and anything that performs I/O from a formula returns `#NOTSUPPORTED` in v1.
