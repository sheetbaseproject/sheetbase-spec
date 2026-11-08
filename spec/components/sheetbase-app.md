---
type: Component
title: sheetbase-app
description: "L4 crate, the eframe desktop binary: windows per document, native menus, file dialogs, OS clipboard, settings persistence, platform glue, the panic guard and the frame loop that batches commands into commits."
tags: [component, crate, app, desktop]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Responsibilities

- `main`: clap parsing ([CLI surface](../cli/surface.md)), logging (`tracing-subscriber`, file
  in the platform log dir), wgpu adapter probe with glow fallback, `eframe::run_native`.
- `app`: `AppState`, frame loop (collect commands, batch, apply, repaint), recent files, dirty
  tracking, autosave of `_sheetbase_UiState`.
- `platform`: macOS menus and Apple events (open document), Windows file associations, Linux
  portal theme; clipboard via `arboard` with the HTML flavour; `rfd` dialogs.
- `guard`: `catch_unwind` around command application, state restore, diagnostics bundle (log
  tail, versions, last 20 commands) for the error bar's copy button.
- `services`: the host closures the UI needs (clipboard, open external, reveal file).

# Dependencies

`eframe 0.37` (`wgpu`, `glow` optional, `accesskit`, `persistence`), `sheetbase-ui`, `sheetbase-store`,
`sheetbase-import`, `sheetbase-core`, `clap 4`, `rfd 0.18`, `arboard 3`, `tracing-subscriber`,
`directories`. `#![deny(unsafe_code)]` with per-item allow for platform glue.

# Size

About 3k lines.

# Requirements carried

REQ-APP-01 to 03, REQ-SEC-04.
