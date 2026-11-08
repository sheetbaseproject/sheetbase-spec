---
type: Plan
title: Open questions
description: Decisions the panel could not close with the information at hand, each with the recommended default that applies until someone overrides it, and what would change the answer.
tags: [plan, open-questions]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

| # | Question | Recommended default | What would change it | Decide by |
|---|---|---|---|---|
| 1 | Should the optional `python` feature (RustPython in a wasm sandbox) be built? | No. Measure first (fixture compile rate, opt-in telemetry). | Compile rate on real documents under 90 percent after the converter is in. | end of M3 |
| 2 | Is `Enter` after commit "stay" (Grist) or "move down" (xldatagrid, Excel)? | Preference, default "stay" to match Grist documents' users; Excel-style users flip it once. | User research in M7 beta. | M7 |
| 3 | Does the Causl mirror track upstream `main` or the release branch? | Release branch (has `node_version`, 0.8.x CHANGELOG). | Upstream merging the release branch back into main (CHANGELOG suggests `chore/512-merge-back` does exactly that). | M0 |
| 4 | Do we expose `read_at`/retention for a UI time-travel debugger? | No for v1; `commit_history_cap = 0`. | A debugging need during M5/M6 that `sb explain` does not cover. | M6 |
| 5 | A pinned formula bar above the grid (xldatagrid, gridcraft) in addition to in-cell editing? | Not in v1; the creator panel shows the formula. | Beta feedback. | M7 |
| 6 | Per-chunk column nodes for very wide, very tall tables? | No; measure `commit_bulk_update_100k` first. | A bench showing dirty-set bitmaps themselves dominate at 1M rows. | M3 |
| 7 | `Int` storage as `i64` with the 32-bit validity check: should we loosen Grist's `is_int_short` and accept 64-bit ints as valid Int? | Keep Grist's rule for compatibility; values outside the range are AltText as in Grist. | A decision to diverge from Grist on types, which would need a flag in `_sheetbase_Settings`. | M1 |
| 8 | Chart rendering through `egui_plot` or the harvested gridcraft `chart` primitives? | `egui_plot` for v1 (less code); revisit if pie/donut fidelity is poor. | Snapshot review in M6. | M6 |
| 9 | Should `sb serve` also speak MCP? | Not in v1; JSON-RPC is enough for agents and MCP wraps it. | A concrete integration asking for it. | post-M8 |
| 10 | Telemetry opt-in default | Off, with a one-time prompt at first `#PYTHON` encounter. | Legal review. | M8 |
| 11 | Windows ARM and Linux ARM binaries | Build them; wgpu and SQLite are fine. | CI runner availability. | M8 |
| 12 | Should the `ReferenceGraph` backend be published or stay test-only? | Published (it is the no-default-features build), documented as not for production. | Nobody uses it. | M8 |
| 13 | Comments (`_grist_Cells`) editing | Read-only in v1. | Beta demand. | M7 |
| 14 | How many undo bundles to keep in `_sheetbase_ActionHistory`? | 1000 or 16 MiB, like Grist. | Documents with huge pastes blowing the cap too fast. | M2 |
| 15 | Should the desktop app ever write `_gristsys_ActionHistory` for a pure-Grist-compatible save? | No; our JSON history travels alongside. Grist ignores unknown tables. | Grist refusing to open documents with unknown tables (it does not today). | M1 |
