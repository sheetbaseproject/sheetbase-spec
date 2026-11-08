---
type: Plan
title: Milestones
description: M0 to M8, each with its deliverables and a measurable exit criterion, ordered so the engine is proven against Grist fixtures before any pixel is drawn.
tags: [plan, milestones]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

| Milestone | Deliverables | Exit criterion |
|---|---|---|
| **M0 Foundations** | workspace skeleton with the eight crates and `xtask layers`; Causl mirror populated and tagged; `sheetbase-graph` with both backends and the differential proptest; `Value` and `ColumnType`; `cargo deny` config; fixture corpus vendored with NOTICE | `cargo xtask ci` green; `facade_overhead_chain_1024` under 5 percent; 1000-case differential proptest passes |
| **M1 Store and model** | SQLite open/save, marshal codec, value codec, migrations 1 to 47, `Document`/`ColumnStore`, `MetaIndex`, `sb info`, `sb schema` | every fixture opens and round-trips (`.sheetbase` save, reopen, identical data); every marshal blob round-trips byte-identically; `open_1m_cells` under 400 ms |
| **M2 Actions** | all user actions, doc actions, inverses, bundles, history table, ACL pipeline, `sb apply`, `sb undo`, `sb history`, `sb serve` | ported `test_useractions`, `test_column_actions`, `test_table_actions`, `test_undo*`, `test_relabeling`, `test_acl_*`, `test_locked_tables` pass; atomicity and inverse proptests pass |
| **M3 Formulas and recalc** | SFL lexer/parser/compiler/interpreter, function library (H and G), relations, formula compute, trigger formulas, lookups, summary tables, cycle groups, display columns, rule columns, `sb check`, `sb formula eval`, `sb explain` | 95 percent of fixture formulas compile; `sb check` reports zero differences on every compiling fixture; the remaining ported sandbox suites pass; engine bench gates met |
| **M4 Import and export** | csv/tsv/xlsx import with `ImportPlan`, csv/tsv/xlsx export, `.grist` save-as with convertibility check, `sb import`, `sb export`, `sb migrate` | `csv_import_100k` under 1.5 s; export of every fixture section matches Grist's `ExportDSV` output for the `Exports.grist` fixture |
| **M5 Grid** | `sheetbase-ui` grid widget: geometry, paint, selection FSM, keyboard, editors for every cell type, clipboard, drag, resize, freeze, new row, context menus, theme, announcer; `sheetbase-app` shell with open/save and one page | all grid `kittest` behaviours green; snapshots at 1x/2x both themes; `grid_paint_900` under 6 ms; `grid_scroll_100k` under 9 ms; contrast test green |
| **M6 Views** | pages, layout, sections, card and card list, chart, linking, sort/filter UI, column filter menu, creator panel (column/widget/page), type converter, find, raw data page, access rules page (read-only), history panel | every fixture document's pages render; `SelectBy*`, `LinkChain`, `FilterLinkChain`, `CardView`, `ChartData` fixtures behave as in Grist (manual checklist + kittest); `page_two_sections` under 12 ms |
| **M7 Polish and compatibility** | import wizard UI, export dialog, document settings, preferences, shortcuts dialog, about with notices, attachments viewer, access rules editor, conditional rule editor, `#PYTHON` converter dialog, error bar and progress, reduced motion | the catalogue's 40 widgets all have tests; a11y check passes on every snapshot; VoiceOver and NVDA walkthrough recorded |
| **M8 Release 1.0** | signed binaries for macOS, Windows, Linux; reproducible build; docs site from the spec; migration telemetry opt-in | 30 days of nightly fuzz with no crash; every performance gate green on the CI runner; the open questions list has no `undecided` rows |

Dependencies: M1 needs M0; M2 needs M1; M3 needs M2; M4 needs M3 (type guessing uses the engine);
M5 needs M2 (it edits data) and benefits from M3; M6 needs M3 and M5; M7 needs M6; M8 needs
everything. M4 and M5 can run in parallel.

The milestones are the exit criteria; the tracker in `sheetbaseproject/sheetbase` is cut
differently. Work is organised as EPICs named with capital letters (`EPIC A` to `EPIC L`), each
with phases that run in order (`A1`, `A2`, ...) and at most five tasks per phase that can run in
parallel (`A1.1`, `A1.2`, ...). One issue per EPIC holds the phases as task lists; one issue per
task holds the goal, the spec references, the acceptance checklist and its blockers. Milestones
map onto EPICs many to many (M0 is A and B, M3 is E and F, M5 is H and I), the mapping and every
issue number are in [the issue map](issue-map.md), and every PR closes an issue.
