---
type: Plan
title: Issue map
description: How the v1 work is tracked in sheetbaseproject/sheetbase as twelve EPICs with sequential phases and parallel tasks, the issue number of every EPIC and task, the mapping back to milestones M0 to M8 and to every requirement id, and the ordering decisions the panel took when cutting the plan.
tags: [plan, issues, tracking]
status: draft
generated: { by: human:spdrman, at: 2026-11-08T18:00:00Z }
---

# The scheme

Work lives in `sheetbaseproject/sheetbase` as EPICs named with capital letters (`EPIC A` to
`EPIC L`). Each EPIC has phases (`A1`, `A2`, ...) that run in order, and each phase has at most
five tasks (`A1.1`, `A1.2`, ...) that can run in parallel. One issue per EPIC carries the phases
as `### A1 <name>` sections holding a task list of `- [ ] #<n>` links; one issue per task carries
the goal, the spec references, the acceptance checklist, the crates touched and its `Blocked by`
and `Blocks` lines. Phases have no issues of their own. That gives 12 EPIC issues plus 77 task
issues, 89 in total, under the 100 ceiling with room for the bugs that will come.

A task is sized for one engineer or one agent over one to three days; a few (the gridcraft
harvest, the 47 migrations) are mechanical and may land as two or three PRs against the one
issue. Every PR closes an issue. Labels: `epic`, `task`, `epic:A` to `epic:L`, and `area:<crate>`
for the eight crates plus `area:xtask` and `area:ci`.

# Decisions made while cutting the plan

**Milestones are not EPICs one to one.** M0 split into A (foundations) and B (the graph facade)
because B's Causl backend waits on the public mirror ([ADR-003](../decisions/adr-003-causl-dependency.md))
and nothing else should wait with it; the reference backend lets D start on time. M2 and M3
became D (actions, undo, access rules), E (the formula language, which is L0 and runs alongside
C and D) and F (the recalc engine that needs both). M5 split into H (the grid over a synthetic
data source) and I (the view model, the shell, the page widgets). The CLI's subcommands land
with the EPIC that enables them, and K owns the contract across them plus `sb serve`.

**The grid starts early, the engine still comes before pixels.** The user wants the xldatagrid
port early; [milestones](milestones.md) orders the engine first. The architecture and performance
roles resolved it like this: EPIC H depends only on types from C1 (`ColumnType`, `WidgetOptions`,
`SectionRec`, `FieldRec`) and on `Value` and `numfmt` from A2, and builds the whole grid over a
`GridDataSource` trait with a synthetic in-memory implementation. The pure layers (selection,
`decide()`, clipboard codecs, the cell registry) are ported test-first exactly as
[ADR-011](../decisions/adr-011-grid-architecture.md) asks, the paint and scroll benches run against
the synthetic source, and the grid meets the engine only in EPIC I, after F has proven the engine
against the fixtures. The cost is that one trait, kept deliberately narrow (row ids, field ids,
formatted text, a style index, a column version), which is what the `view:` nodes expose anyway,
so the rework risk when I replaces it with the view store is small. The dissent (recorded):
the architecture role would have preferred the view model first so the trait is derived rather
than guessed; it accepted the narrow-trait bound as sufficient.

**Access rules stay in D, not deferred.** [ADR-013](../decisions/adr-013-acl-scope.md) holds:
parsing and action-side enforcement are D3, read-side pruning and censoring are I1.1 because
they are view nodes.

# EPICs and dependencies

| EPIC | Name | Milestones | Phases | Tasks | Depends on |
|---|---|---|---|---|---|
| A (#78) | Foundations | M0 | 2 | 5 | nothing |
| B (#79) | Graph facade | M0 | 2 | 4 | A phase A1; B2 also needs the Causl mirror tagged |
| C (#80) | Document model and store | M1 | 3 | 10 | A phase A2 |
| D (#81) | Actions, undo and access rules | M2 | 3 | 8 | C phase C1, B phase B1 |
| E (#82) | Formula language (SFL) | M3 | 4 | 8 | A phase A2; E4 needs C phase C2 |
| F (#83) | Recalc engine | M3 | 3 | 8 | D phase D2, E phase E2; F3 benches need B phase B2 |
| G (#84) | Import and export | M4 | 2 | 4 | F phase F1, E phase E4 |
| H (#85) | Grid widget | M5 | 3 | 11 | A phase A2, C phase C1 |
| I (#86) | Views and desktop shell | M5, M6 | 3 | 9 | F phase F2, H phase H2, D phase D3 |
| J (#87) | Polish and compatibility | M7 | 2 | 4 | I phase I3, G phase G2 |
| K (#88) | Headless and agent surface | M2 to M4 (CLI) | 2 | 3 | D phase D2, F phase F3, G phase G2 |
| L (#89) | Release 1.0 | M8 | 2 | 3 | J and K, every phase |

The Causl mirror (`sheetbaseproject/causl-engine-core`, tag `v0.8.1+sheetbase.1`) is a
maintainer action, not a task; B2.1 (#8), B2.2 (#9) and F3.2 (#43) say they wait on it.

# Tasks

The requirements column lists every requirement id a task's text or acceptance criteria name.

| Id | Title | Issue | Milestone | Requirements |
|---|---|---|---|---|
| **EPIC A** | **Foundations** | #78 | M0 | |
| A1 | Workspace and gates | | | |
| A1.1 | Workspace with the eight crates, layer table and xtask ci | #1 | | REQ-GRAPH-01, REQ-SEC-01 |
| A1.2 | Fixture corpus with notices and xtask fixtures refresh | #2 | |  |
| A1.3 | Bench harness and cargo xtask bench --gate | #3 | | REQ-PERF-03 |
| A2 | Value model and the gridcraft harvest | | | |
| A2.1 | Value, CellError, ColumnTypeKind and the Failure trait | #4 | |  |
| A2.2 | Harvest gridcraft numfmt, functions, value compat and date serials | #5 | |  |
| **EPIC B** | **Graph facade** | #79 | M0 | |
| B1 | Contract and reference backend | | | |
| B1.1 | Graph trait, registry with namespaces, and GraphError | #6 | | REQ-GRAPH-03, REQ-GRAPH-04 |
| B1.2 | ReferenceGraph backend and the shared contract tests | #7 | | REQ-GRAPH-02 |
| B2 | Causl backend and differential tests | | | |
| B2.1 | CauslGraph backend over the public mirror, with the explain feature | #8 | | REQ-GRAPH-01 |
| B2.2 | Differential proptest and the facade overhead benches | #9 | | REQ-GRAPH-01, REQ-GRAPH-02, REQ-GRAPH-05 |
| **EPIC C** | **Document model and store** | #80 | M1 | |
| C1 | In-memory model and wire types | | | |
| C1.1 | ColumnType, Document, Table, Column and WidgetOptions | #10 | | REQ-MODEL-01, REQ-MODEL-02 |
| C1.2 | ColumnStore with typed columns, RowSet and DeltaLog | #11 | | REQ-MODEL-03 |
| C1.3 | MetaIndex over every _grist_ table and the schema consistency check | #12 | | REQ-MODEL-01, REQ-MODEL-05 |
| C1.4 | Wire format and the DocAction, UserAction and ActionBundle data types | #13 | | REQ-ACTION-04, REQ-MODEL-02 |
| C2 | SQLite codec, load and save | | | |
| C2.1 | Marshal codec with caps and a fuzz target | #14 | | REQ-SEC-03, REQ-STORE-03 |
| C2.2 | Store codec, schema-47 DDL and Store::create | #15 | | REQ-STORE-01, REQ-STORE-03 |
| C2.3 | Load path with defensive pragmas, errors and the open benches | #16 | | REQ-PERF-02, REQ-SEC-03, REQ-STORE-06 |
| C2.4 | Save path, action history table and save-as with the convertibility check | #17 | | REQ-IO-03, REQ-STORE-01, REQ-STORE-04, REQ-STORE-05 |
| C3 | Migrations, the sb skeleton and the fixture harness | | | |
| C3.1 | Migrations 1 to 47 with the fixture families as golden tests | #18 | | REQ-STORE-02 |
| C3.2 | sb skeleton (info, schema, version) and the fixture round-trip harness | #19 | | REQ-CLI-01, REQ-CLI-02, REQ-MODEL-01, REQ-STORE-01 |
| **EPIC D** | **Actions, undo and access rules** | #81 | M2 | |
| D1 | Doc actions, bundles and the pipeline | | | |
| D1.1 | Apply doc actions with inverses, staging overlay and rollback | #20 | | REQ-ACTION-02 |
| D1.2 | Engine::apply_user_actions pipeline, bundles, atomicity and the golden harness | #21 | | REQ-ACTION-02, REQ-ACTION-03 |
| D2 | User actions and undo | | | |
| D2.1 | Record user actions, temp row ids, type guessing and relabeling | #22 | | REQ-ACTION-01, REQ-MODEL-04 |
| D2.2 | Column user actions and the _grist_Tables_column hooks | #23 | | REQ-ACTION-01 |
| D2.3 | Table, view and section user actions, the remaining hooks and schema consistency | #24 | | REQ-ACTION-01, REQ-MODEL-05 |
| D2.4 | Undo and redo through the pipeline, and sb apply, undo, redo, history | #25 | | REQ-ACTION-02, REQ-ACTION-04, REQ-STORE-04 |
| D3 | Access rules | | | |
| D3.1 | Access rule grammars, aclFormulaParsed round trip and user attributes | #26 | | REQ-ACL-01, REQ-SEC-03 |
| D3.2 | Access rule enforcement in the pipeline, defaults, SPECIAL, locked tables and --as-user | #27 | | REQ-ACL-02, REQ-ACL-03 |
| **EPIC E** | **Formula language (SFL)** | #82 | M3 | |
| E1 | Tokenizer, parser and compiler | | | |
| E1.1 | SFL tokenizer and parser with spans, and the parse fuzz target | #28 | | REQ-FORMULA-04, REQ-SEC-03 |
| E1.2 | SFL compiler: lazy args, implicit return, name resolution, Program and parse_grist_names | #29 | | REQ-FORMULA-06, REQ-FORMULA-07 |
| E2 | Interpreter, records and dates | | | |
| E2.1 | Interpreter core with limits, Python semantics, builtins and the eval benches | #30 | | REQ-FORMULA-04, REQ-FORMULA-08, REQ-SEC-02 |
| E2.2 | RecordSource, Record and RecordSet objects, Table lookups and the lookup bench | #31 | | REQ-FORMULA-08 |
| E2.3 | Dates over jiff with moment-compatible formatting and parsing | #32 | |  |
| E3 | Function library and the eval command | | | |
| E3.1 | Grist function wrappers over the harvested library and the registry test | #33 | | REQ-FORMULA-03 |
| E3.2 | Grist-only functions, the doctest extraction, sb formula eval and completions | #34 | | REQ-ENGINE-06, REQ-FORMULA-03 |
| E4 | Classification and conversion of imported formulas | | | |
| E4.1 | Formula classification on open, the #PYTHON cell, the formula report and the converter | #35 | | REQ-FORMULA-02, REQ-FORMULA-05 |
| **EPIC F** | **Recalc engine** | #83 | M3 | |
| F1 | Formula compute, relations and triggers | | | |
| F1.1 | FormulaCompute with relations, DeltaLog, the core RecordSource and the engine proptests | #36 | | REQ-ENGINE-01, REQ-ENGINE-02, REQ-ENGINE-03 |
| F1.2 | Renames rewriting formulas, compile error handling and trigger formulas | #37 | | REQ-ENGINE-04, REQ-FORMULA-06 |
| F2 | Lookups, summaries, cycles and helper columns | | | |
| F2.1 | Lookup index nodes, sorted indexes, find.*, and the lookup fan-out bench | #38 | | REQ-ENGINE-04, REQ-PERF-01 |
| F2.2 | Summary tables: helper node, group column, auto-created rows and auto-remove | #39 | | REQ-ENGINE-04, REQ-PERF-01 |
| F2.3 | Cycle groups with the lazy per-cell evaluator, and PREVIOUS, NEXT, RANK | #40 | | REQ-ENGINE-05 |
| F2.4 | Display columns, rule columns, two-way references and the remaining golden ports | #41 | | REQ-ENGINE-04, REQ-MODEL-02, REQ-VIEW-04 |
| F3 | Verification, benches and determinism | | | |
| F3.1 | sb check with --fix, sb recalc and sb explain | #42 | | REQ-CLI-03, REQ-ENGINE-01, REQ-FORMULA-01 |
| F3.2 | Engine bench suite with gates, memory, determinism, progress and cancel | #43 | | REQ-ENGINE-06, REQ-ENGINE-07, REQ-PERF-01, REQ-PERF-02, REQ-PERF-03 |
| **EPIC G** | **Import and export** | #84 | M4 | |
| G1 | Import | | | |
| G1.1 | Format sniffing, csv/tsv import plan with type guessing, caps and the csv bench | #44 | | REQ-IO-01, REQ-IO-04, REQ-SEC-03 |
| G1.2 | xlsx import plan through calamine with harvested style and feature mapping | #45 | | REQ-IO-02, REQ-IO-04 |
| G1.3 | Executing an ImportPlan and sb import | #46 | | REQ-IO-01 |
| G2 | Export and migrate | | | |
| G2.1 | csv, tsv, xlsx and json export, sb export, sb migrate and the Exports.grist comparison | #47 | | REQ-ACL-02, REQ-IO-02, REQ-IO-03 |
| **EPIC H** | **Grid widget** | #85 | M5 | |
| H1 | Pure layers, tested without pixels | | | |
| H1.1 | Theme tokens with measured WCAG contrast, fonts and icons | #48 | | REQ-UI-07 |
| H1.2 | Selection state, reducers, FSM, pointer decisions and drag-select math | #49 | | REQ-UI-01, REQ-UI-03 |
| H1.3 | Keyboard decide(), the interaction reducer, commit advance and the command registry | #50 | | REQ-UI-01, REQ-UI-02 |
| H1.4 | Clipboard codecs: TSV, Grist HTML flavour, bounded parser and paste tiling | #51 | | REQ-SEC-03, REQ-UI-01, REQ-UI-04 |
| H1.5 | Cell type registry, formatting, typed input parsing and the format cache | #52 | | REQ-UI-06 |
| H2 | Geometry, paint, interaction and editors | | | |
| H2.1 | Geo geometry, hit testing, pixel snapping and the synthetic GridDataSource | #53 | | REQ-UI-08 |
| H2.2 | Paint pipeline, cell renderers, galley cache, headers, gutter, new-row line and snapshots | #54 | | REQ-UI-06, REQ-UI-08, REQ-UI-10 |
| H2.3 | Drag state machine, resize, freeze, fill handle, autofit and context menus | #55 | | REQ-UI-10 |
| H2.4 | In-cell editors for every cell type and the formula editor | #56 | | REQ-UI-01, REQ-UI-06 |
| H3 | Accessibility, scale and frame benches | | | |
| H3.1 | AccessKit grid tree, the announcer and tests/a11y_grid.rs | #57 | | REQ-A11Y-01, REQ-A11Y-02 |
| H3.2 | Grid frame benches with gates, idle repaint, interface scale, reduced motion and the trace audit | #58 | | REQ-PERF-03, REQ-PERF-04, REQ-PERF-06, REQ-UI-01, REQ-UI-09 |
| **EPIC I** | **Views and desktop shell** | #86 | M5, M6 | |
| I1 | View model nodes and linking | | | |
| I1.1 | View nodes: rows, cells, styles, cursor, layout, pages, the ViewStore and read-side access rules | #59 | | REQ-ACL-02, REQ-VIEW-01, REQ-VIEW-03, REQ-VIEW-04 |
| I1.2 | Linking: all seven link types as view:section:{id}:linkfilter | #60 | | REQ-VIEW-02 |
| I2 | Desktop shell | | | |
| I2.1 | eframe app shell, frame loop, DocView over the ViewStore and the edit latency gate | #61 | | REQ-PERF-05, REQ-VIEW-03 |
| I2.2 | Open, save, save-as, recent files, windows per document, file associations and startup | #62 | | REQ-APP-01, REQ-APP-03 |
| I2.3 | Panic guard, error bar, progress bar with cancel, and the OS clipboard | #63 | | REQ-ENGINE-07, REQ-SEC-04, REQ-UI-04 |
| I3 | Pages, sections and panels | | | |
| I3.1 | Page tree, raw data page, page layout, section frame, new table and page dialogs, link picker | #64 | | REQ-UI-05, REQ-VIEW-01 |
| I3.2 | Card view, card list, chart view and the custom widget placeholder | #65 | | REQ-UI-05, REQ-VIEW-01 |
| I3.3 | Sort and filter bar, column filter menu, filter condition dialog, column chooser and find | #66 | | REQ-UI-05, REQ-UI-10 |
| I3.4 | Creator panel, type converter, history panel, read-only access rules page, tooltip and status bar | #67 | | REQ-ACL-03, REQ-UI-05 |
| **EPIC J** | **Polish and compatibility** | #87 | M7 | |
| J1 | Dialogs and editors | | | |
| J1.1 | Import wizard and export dialog | #68 | | REQ-A11Y-02, REQ-IO-01, REQ-IO-02, REQ-UI-05 |
| J1.2 | Document settings, preferences, shortcuts dialog, about with notices and the attachment viewer | #69 | | REQ-APP-02, REQ-UI-05 |
| J1.3 | Access rules editor, conditional rule editor, #PYTHON converter dialog and the save-as-grist explanation | #70 | | REQ-FORMULA-05, REQ-IO-03, REQ-UI-05 |
| J2 | Catalogue and accessibility audit | | | |
| J2.1 | Catalogue audit, accessibility check on every snapshot, focus trapping, screen reader walkthroughs and comments display | #71 | | REQ-A11Y-02, REQ-A11Y-03, REQ-UI-05 |
| **EPIC K** | **Headless and agent surface** | #88 | M2 to M4 (CLI) | |
| K1 | sb serve | | | |
| K1.1 | sb serve: JSON-RPC 2.0 over stdio with the document and formula methods | #72 | | REQ-AGENT-01 |
| K1.2 | doc.subscribe notifications, doc.schema --compact, doc.describe and the published action schema | #73 | | REQ-ACTION-04, REQ-AGENT-02 |
| K2 | The CLI contract | | | |
| K2.1 | CLI integration suite: every subcommand, one JSON document, exit codes and the binary size gate | #74 | | REQ-CLI-01, REQ-CLI-02, REQ-CLI-04 |
| **EPIC L** | **Release 1.0** | #89 | M8 | |
| L1 | Hardening | | | |
| L1.1 | Nightly fuzz job with the 30-day gate, and every performance gate on the reference runner | #75 | | REQ-PERF-03, REQ-SEC-02 |
| L2 | Ship | | | |
| L2.1 | Reproducible signed builds for macOS, Windows and Linux, including ARM | #76 | |  |
| L2.2 | Docs site from the spec, telemetry opt-in, open questions closed and the spec marked stable | #77 | |  |

# Requirement coverage

Every requirement id in `spec/requirements/` appears in at least one task. Nothing was left out on purpose; the `should` and `could` rows (REQ-GRAPH-05, REQ-ENGINE-07, REQ-FORMULA-07, REQ-FORMULA-08, REQ-CLI-04, REQ-AGENT-02, REQ-APP-03, REQ-STORE-06, REQ-UI-09, REQ-A11Y-03, REQ-PERF-06) sit in tasks with their `must` neighbours and may slip to v1.1 with a recorded reason, as the requirements overview allows. Features outside the requirement ids that the scope page defers (`.xls`/`.ods` import, comment editing, attachment upload, a pinned formula bar, the optional `python` feature, MCP over `sb serve`) have no task and stay on [open questions](open-questions.md).

| Requirement | Tasks |
|---|---|
| REQ-ACL-01 | D3.1 (#26) |
| REQ-ACL-02 | D3.2 (#27), G2.1 (#47), I1.1 (#59) |
| REQ-ACL-03 | D3.2 (#27), I3.4 (#67) |
| REQ-VIEW-01 | I1.1 (#59), I3.1 (#64), I3.2 (#65) |
| REQ-VIEW-02 | I1.2 (#60) |
| REQ-VIEW-03 | I1.1 (#59), I2.1 (#61) |
| REQ-VIEW-04 | F2.4 (#41), I1.1 (#59) |
| REQ-ACTION-01 | D2.1 (#22), D2.2 (#23), D2.3 (#24) |
| REQ-ACTION-02 | D1.1 (#20), D1.2 (#21), D2.4 (#25) |
| REQ-ACTION-03 | D1.2 (#21) |
| REQ-ACTION-04 | C1.4 (#13), D2.4 (#25), K1.2 (#73) |
| REQ-ENGINE-01 | F1.1 (#36), F3.1 (#42) |
| REQ-ENGINE-02 | F1.1 (#36) |
| REQ-ENGINE-03 | F1.1 (#36) |
| REQ-ENGINE-04 | F1.2 (#37), F2.1 (#38), F2.2 (#39), F2.4 (#41) |
| REQ-ENGINE-05 | F2.3 (#40) |
| REQ-ENGINE-06 | E3.2 (#34), F3.2 (#43) |
| REQ-ENGINE-07 | F3.2 (#43), I2.3 (#63) |
| REQ-GRAPH-01 | A1.1 (#1), B2.1 (#8), B2.2 (#9) |
| REQ-GRAPH-02 | B1.2 (#7), B2.2 (#9) |
| REQ-GRAPH-03 | B1.1 (#6) |
| REQ-GRAPH-04 | B1.1 (#6) |
| REQ-GRAPH-05 | B2.2 (#9) |
| REQ-FORMULA-01 | F3.1 (#42) |
| REQ-FORMULA-02 | E4.1 (#35) |
| REQ-FORMULA-03 | E3.1 (#33), E3.2 (#34) |
| REQ-FORMULA-04 | E1.1 (#28), E2.1 (#30) |
| REQ-FORMULA-05 | E4.1 (#35), J1.3 (#70) |
| REQ-FORMULA-06 | E1.2 (#29), F1.2 (#37) |
| REQ-FORMULA-07 | E1.2 (#29) |
| REQ-FORMULA-08 | E2.1 (#30), E2.2 (#31) |
| REQ-IO-01 | G1.1 (#44), G1.3 (#46), J1.1 (#68) |
| REQ-IO-02 | G1.2 (#45), G2.1 (#47), J1.1 (#68) |
| REQ-IO-03 | C2.4 (#17), G2.1 (#47), J1.3 (#70) |
| REQ-IO-04 | G1.1 (#44), G1.2 (#45) |
| REQ-CLI-01 | C3.2 (#19), K2.1 (#74) |
| REQ-CLI-02 | C3.2 (#19), K2.1 (#74) |
| REQ-CLI-03 | F3.1 (#42) |
| REQ-CLI-04 | K2.1 (#74) |
| REQ-AGENT-01 | K1.1 (#72) |
| REQ-AGENT-02 | K1.2 (#73) |
| REQ-SEC-01 | A1.1 (#1) |
| REQ-SEC-02 | E2.1 (#30), L1.1 (#75) |
| REQ-SEC-03 | C2.1 (#14), C2.3 (#16), D3.1 (#26), E1.1 (#28), G1.1 (#44), H1.4 (#51) |
| REQ-SEC-04 | I2.3 (#63) |
| REQ-APP-01 | I2.2 (#62) |
| REQ-APP-02 | J1.2 (#69) |
| REQ-APP-03 | I2.2 (#62) |
| REQ-PERF-01 | F2.1 (#38), F2.2 (#39), F3.2 (#43) |
| REQ-PERF-02 | C2.3 (#16), F3.2 (#43) |
| REQ-PERF-03 | A1.3 (#3), F3.2 (#43), H3.2 (#58), L1.1 (#75) |
| REQ-PERF-04 | H3.2 (#58) |
| REQ-PERF-05 | I2.1 (#61) |
| REQ-PERF-06 | H3.2 (#58) |
| REQ-MODEL-01 | C1.1 (#10), C1.3 (#12), C3.2 (#19) |
| REQ-MODEL-02 | C1.1 (#10), C1.4 (#13), F2.4 (#41) |
| REQ-MODEL-03 | C1.2 (#11) |
| REQ-MODEL-04 | D2.1 (#22) |
| REQ-MODEL-05 | C1.3 (#12), D2.3 (#24) |
| REQ-STORE-01 | C2.2 (#15), C2.4 (#17), C3.2 (#19) |
| REQ-STORE-02 | C3.1 (#18) |
| REQ-STORE-03 | C2.1 (#14), C2.2 (#15) |
| REQ-STORE-04 | C2.4 (#17), D2.4 (#25) |
| REQ-STORE-05 | C2.4 (#17) |
| REQ-STORE-06 | C2.3 (#16) |
| REQ-UI-01 | H1.2 (#49), H1.3 (#50), H1.4 (#51), H2.4 (#56), H3.2 (#58) |
| REQ-UI-02 | H1.3 (#50) |
| REQ-UI-03 | H1.2 (#49) |
| REQ-UI-04 | H1.4 (#51), I2.3 (#63) |
| REQ-UI-05 | I3.1 (#64), I3.2 (#65), I3.3 (#66), I3.4 (#67), J1.1 (#68), J1.2 (#69), J1.3 (#70), J2.1 (#71) |
| REQ-UI-06 | H1.5 (#52), H2.2 (#54), H2.4 (#56) |
| REQ-UI-07 | H1.1 (#48) |
| REQ-UI-08 | H2.1 (#53), H2.2 (#54) |
| REQ-UI-09 | H3.2 (#58) |
| REQ-UI-10 | H2.2 (#54), H2.3 (#55), I3.3 (#66) |
| REQ-A11Y-01 | H3.1 (#57) |
| REQ-A11Y-02 | H3.1 (#57), J1.1 (#68), J2.1 (#71) |
| REQ-A11Y-03 | J2.1 (#71) |
