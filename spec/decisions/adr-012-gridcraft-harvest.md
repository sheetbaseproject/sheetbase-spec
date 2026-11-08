---
type: Decision
title: "ADR-012: Harvest gridcraft file by file under Apache-2.0 with notices; never its A1 model, chrome or forks"
description: About 20k lines of gridcraft (number formats, functions, Value and coercion, theme tokens and contrast test, selection glide, font discovery, display cache, HTML clipboard) are copied verbatim with attribution; the formula parser skeleton, calc graph index, style model, grid geometry and paint pipeline, command and undo architecture, xlsx and csv readers are adapted; everything Excel-specific is rejected.
tags: [decision, licence, gridcraft]
status: draft
decision_id: ADR-012
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: gridcraft-notice
    resource: https://github.com/storytold/gridcraft/blob/main/NOTICE
    title: gridcraft NOTICE ("Copyright (c) 2026 ArtCraft Team and the GridCraft contributors / Licensed under the MIT License or the Apache License, Version 2.0, at your option")
  - id: gridcraft-brand
    resource: https://github.com/storytold/gridcraft/tree/main/docs/brand
    title: docs/brand/LICENSE-brand.txt (ArtCraft marks not open source; forks must remove them)
---

# Context

gridcraft is a 240k-line clean-room Excel clone in Rust, dual `MIT OR Apache-2.0`, no CLA, no
per-file headers, with a NOTICE file and a trademark carve-out.[^gridcraft-notice][^gridcraft-brand]
It depends on forks of egui and winit and on `storytold/craft-libs`. Its engine is A1-addressed
and bound to a `Workbook` type. It moves fast (several commits a day), so anything copied is a
snapshot.

# Decision

Policy:

1. **Take under Apache-2.0.** Each copied file keeps a header naming origin path and commit,
   the gridcraft copyright line, and the modifications made. `sheetbase/NOTICE` reproduces the
   gridcraft project line. `third_party/HARVEST.md` lists every copied file.
2. **Copy verbatim** only code that is model-free: `crates/numfmt/**`, `crates/functions/**`,
   `crates/core/src/{value,date,color,parse}.rs`, `crates/engine/src/display.rs`,
   `crates/engine/src/clip_html.rs`, `crates/ui-egui/src/selection_glide.rs`,
   `crates/ui-egui/src/theme.rs` (structure and `contrast()` and the WCAG test, with our token
   values), `crates/ui-egui/src/theme/{font_setup,font_fallback}.rs`, `crates/ui-egui/src/fonts.rs`,
   `crates/ui-egui/src/desktop_theme.rs`, `crates/ui-egui/src/code_editor.rs`,
   `xtask/src/layers.rs`.
3. **Adapt** (design and large parts survive, A1 removed): formula lexer/parser/AST skeleton
   (`LET`/`LAMBDA`/`Invoke`, auto-close parens, `same_name` folding), `calc/src/recalc/graph.rs`
   `Intervals` index (for row-range relations), evaluator bounds (`MAX_DEPTH`, fuel, stack
   budget), `model/src/style.rs`, `model/src/features.rs` (table, CF and validation types),
   `ui-egui/src/grid/{geo,quadrant,cell_paint,show,interact,keyboard,selection,menus}.rs`,
   `ui-egui/src/grid/editor.rs` and `formula_bar.rs`, `ui-egui/src/app/clipboard.rs`,
   `engine/src/{lib,cmd}.rs` (command registry with `enabled`/`run`, journal, panic guard),
   `engine/src/selection.rs`, `xlsx/src/{read,sheet_read,styles,csv}.rs`,
   `apps/gridcraft/src/{graphics,native_menu,apple_events}.rs`, `apps/gridcraft-cli` pattern,
   `crates/mcp` and the control channel if `sb serve` wants a JSON-RPC skeleton.
4. **Reject**: A1 addressing (`addr.rs`, `adjust.rs`, spill, `TRIMRANGE`, `OFFSET`/`INDIRECT`
   specials), `Workbook`/`Sheet`/`CellStore`, pivots, macros, Python cells, page layout,
   printing, charts' `resolve.rs`, the ribbon, backstage, dialogs, keytips, i18n files, the
   egui/winit forks, craft-libs, packaging, brand assets, assistant-instruction files, CI workflows.

The complete file-level list is [the harvest list](../references/gridcraft-harvest.md).

# Alternatives

**Harvest nothing, write everything.** Clean provenance. Lost: `numfmt` and `functions` alone
are 18k tested lines we would otherwise reproduce from the same ECMA-376 text, slower and worse.

**Depend on gridcraft crates as git dependencies instead of copying.** Lost: they pin an egui
fork through `[patch.crates-io]` that would infect our build, `calc` and `xlsx` are bound to
`Workbook`, and their velocity means our build would break weekly.

**Also harvest `crates/pdf`.** Zero-dependency PDF writer, nice for export. Deferred: no PDF
export in v1; the Adobe AFM and Unicode notices it carries must come with it when it does.

# Consequences

- The risk that the "clean-room" claim is weaker than stated (no CLA, 240k lines in a month) is
  recorded in [ADR-001](adr-001-licence.md); we harvest only algorithmic code whose independent
  derivation from public standards is plausible (number formats from ECMA-376 section 18.8.31,
  functions from the ECMA-376 formula spec), not UI chrome that resembles Excel's.
- `functions` names are Excel names. Grist's function list overlaps (SUM, IF, VLOOKUP, ...) and
  differs (`lookupRecords`, `CONTAINS`, `PEEK`, `RECORD`, `MOONPHASE`). The wrapper table in
  [functions](../formula/functions.md) maps each Grist name to a harvested implementation or to
  new code.

[^gridcraft-notice]: gridcraft NOTICE ("Copyright (c) 2026 ArtCraft Team and the GridCraft contributors / Licensed under the MIT License or the Apache License, Version 2.0, at your option")
[^gridcraft-brand]: docs/brand/LICENSE-brand.txt (ArtCraft marks not open source; forks must remove them)
