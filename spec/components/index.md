# Component

* [sheetbase-app](sheetbase-app.md) - L4 crate, the eframe desktop binary: windows per document, native menus, file dialogs, OS clipboard, settings persistence, platform glue, the panic guard and the frame loop that batches commands into commits.
* [sheetbase-cli](sheetbase-cli.md) - L4 crate, the headless binary sb: info, check, recalc, export, import, apply, undo, redo, history, formula eval, migrate, explain, schema, bench, fixtures, serve (JSON-RPC over stdio).
* [sheetbase-core](sheetbase-core.md) - L1 crate with the Document, ColumnStore, metadata index, user and doc actions, the engine (pipeline, computes, relations, lookups, summaries, cycle groups, trigger formulas), access rules and the view model.
* [sheetbase-formula](sheetbase-formula.md) - L0 crate holding Value, the SFL lexer/parser/compiler/interpreter, the function library, number formats and date handling; no dependency on the document model.
* [sheetbase-graph](sheetbase-graph.md) - L0 crate exposing the Graph facade trait with the CauslGraph backend (feature causl, default) over the public mirror and the ReferenceGraph oracle backend; string ids, namespaces, tracked reads, commits, subscriptions.
* [sheetbase-import](sheetbase-import.md) - L2 crate for opening foreign documents (.grist with formula classification), importing csv/tsv/xlsx through an ImportPlan, and exporting csv/tsv/xlsx.
* [sheetbase-spec (this bundle)](sheetbase-spec-repo.md) - The specification repo: the OKF bundle under spec/, the validator under tools/, and the rules for changing it.
* [sheetbase-store](sheetbase-store.md) - L2 crate for SQLite persistence: open and save with the Grist layout, value codec with marshal, migrations 1 to 47, action history, the _sheetbase_* tables.
* [sheetbase-ui](sheetbase-ui.md) - L3 crate of egui widgets: the grid, cards, chart, pages, creator panel, menus, dialogs, cell renderers and editors, theme, announcer, command registry; testable with egui_kittest without a window.

# Overview

* [About the components](_about.md) - One concept per crate (and one for the spec repo): purpose, public API surface, dependencies, size estimate, and which requirements it carries.
