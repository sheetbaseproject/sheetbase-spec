---
type: Overview
title: Out of scope for v1
description: Features deliberately not in v1, each with the reason and what would have to be true to bring it in.
tags: [overview, scope]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

| Not in v1 | Why | What brings it in |
|---|---|---|
| Multi-user collaboration, a server, real-time sync | Needs a network protocol, auth and per-user action filtering, all of which Grist does in `GranularAccess.ts` on the server side. Doing it right doubles the project. The action bundle format is kept compatible so a later server can replay. [ADR-014](../decisions/adr-014-no-server-v1.md). | A `sheetbase-server` crate once the desktop engine is stable (M8+). |
| A web build (wasm) | egui runs in wasm, but SQLite, file dialogs, the clipboard HTML flavour and attachments all need a different host. | A `sheetbase-web` crate with an IndexedDB store, after v1. |
| Running Grist's Python formulas | Embedding RustPython (0.6.0, MIT) is possible but it is a 2 MB+ interpreter with a weak sandbox story, slow startup and `f64`-only interop with our value model. [ADR-007](../decisions/adr-007-formula-language.md). | An opt-in `python` feature of `sheetbase-formula` behind a wasm sandbox, only if migration telemetry shows the subset misses a lot. |
| Custom widgets (`parentKey = 'custom'`) and Forms | They are iframes with a plugin API. No browser engine in v1. | A webview widget (wry) behind a feature flag. |
| Comments editing, attachments upload, `_grist_Shares` | Preserved, not edited. Each is UI work with no engine risk; cut for schedule. | M7 polish. |
| Excel formula compatibility (A1 references, `=SUM(A1:B2)`) | The product is relational, not a cell grid. gridcraft's function library is harvested for the *functions*, never for A1 addressing. [ADR-012](../decisions/adr-012-gridcraft-harvest.md). | Never, by design. |
| Pivot tables, macros, VBA, Python cells, page layout, printing to PDF | Excel features that Grist does not have either. | Not planned. |
| On-demand tables (`_grist_Tables.onDemand`) | A server-side SQL passthrough feature. Preserved as a flag, treated as a normal table. | With the server. |
| `REQUEST()`, `WEBSERVICE`-style network from formulas | Formulas are untrusted and the sandbox has no I/O. | Not planned for formulas; agents use `sb serve` instead. |
| Importing `.xls`, `.ods`, encrypted workbooks | calamine reads `.xls` and `.ods`, so the cost is low, but the mapping UI is the same as `.xlsx` and that is already in. | M6 if time allows. |
| Mobile and touch-first layouts | egui supports touch; the grid's selection model assumes a pointer and a keyboard. | After v1. |
