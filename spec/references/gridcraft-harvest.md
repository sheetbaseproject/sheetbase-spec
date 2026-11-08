---
type: Reference
title: gridcraft harvest list
description: File-level list of what sheetbase copies, adapts or rejects from storytold/gridcraft at the audited commit, with the destination and reason, under the Apache-2.0 branch of its MIT OR Apache-2.0 licence.
tags: [references, gridcraft, licence]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: gridcraft
    resource: https://github.com/storytold/gridcraft
    title: storytold/gridcraft main, audited 2026-11-08 (workspace 0.16.0, edition 2024, rust-version 1.95, MIT OR Apache-2.0)
---

Licence compliance per [ADR-012](../decisions/adr-012-gridcraft-harvest.md): taken under
Apache-2.0; each copied file keeps a header with origin path and commit, the line "Copyright (c)
2026 ArtCraft Team and the GridCraft contributors", and a modification note; `sheetbase/NOTICE`
reproduces gridcraft's project notice; no trademark material. The commit hash is pinned in
`third_party/HARVEST.md` when the copy is made (M0).[^gridcraft]

| gridcraft path | sheetbase destination | Action | Reason |
|---|---|---|---|
| `LICENSE-MIT`, `LICENSE-APACHE`, `NOTICE` (project line) | `third_party/gridcraft/`, `NOTICE` | copy | attribution |
| `docs/brand/*`, `assets/app-icon/*`, `packaging/*` | none | reject | trademarks and their identifiers |
| `AGENTS.md` and other assistant-instruction files, `contributors/*`, `.github/*`, `.coderabbit.yaml`, `sonar-project.properties`, `ROADMAP.md` | none | reject | their process |
| `Cargo.toml` `[patch.crates-io]` egui/winit forks, `craft-libs` git deps | none | reject | [ADR-010](../decisions/adr-010-egui-upstream.md) |
| `crates/core/src/value.rs` | `sheetbase-formula/src/value/excel_compat.rs` | copy, adapt | coercion, 15-digit compare, `number_to_text`, `CellError` codes used by harvested functions; our `Value` is the primary type |
| `crates/core/src/date.rs` | `sheetbase-formula/src/date/serial.rs` | copy | 1900/1904 serials for Excel-compatible date functions |
| `crates/core/src/color.rs` | `sheetbase-import/src/xlsx/palette.rs` | copy | indexed palette for xlsx import |
| `crates/core/src/parse.rs` | `sheetbase-ui/src/cells/parse_input.rs` | copy, adapt | typed input parsing on cell entry; en-US only, locale later |
| `crates/core/src/addr.rs` | `sheetbase-import/src/xlsx/a1.rs` (only `col_to_letters`/`letters_to_col`) | adapt | import needs column letters; nothing else |
| `crates/numfmt/**` | `sheetbase-formula/src/numfmt/` (own module, same tests) | copy | number format engine for display and `TEXT()` |
| `crates/functions/**` | `sheetbase-formula/src/functions/excel/` | copy | 491 functions over `Value`; wrapped to Grist names |
| `crates/formula/src/lexer.rs`, `parser.rs`, `ast.rs`, `lib.rs` | `sheetbase-formula/src/sfl/` (design reference) | adapt | Pratt skeleton, literals, `LET`/`LAMBDA`/`Invoke`, auto-close parens, `same_name`; SFL is Python syntax so most code is rewritten |
| `crates/formula/src/adjust.rs`, `printer.rs`, `input.rs` | none | reject | A1 reference shifting, R1C1 printing, Spanish aliases |
| `crates/calc/src/recalc/graph.rs` (`Intervals`) | `sheetbase-core/src/engine/intervals.rs` | adapt | row-range index for `Relation` maps over contiguous ranges |
| `crates/calc/src/recalc.rs`, `recalc/pass_host.rs` | design reference only | adapt | dirty closure and on-demand host ideas; Causl replaces the scheduler |
| `crates/calc/src/eval.rs`, `eval/*` | `sheetbase-formula/src/sfl/interp/limits.rs` | adapt | `MAX_DEPTH`, fuel, stack budget pattern; `Ev`/`Area` rejected |
| `crates/calc/src/precision.rs`, `trimrange.rs` | none | reject | Excel-only |
| `crates/model/src/style.rs` | `sheetbase-import/src/xlsx/style.rs` | adapt | font/fill/border/alignment for xlsx import and export mapping to Grist widgetOptions |
| `crates/model/src/features.rs` (Table, CF, Validation, Filter) | `sheetbase-import/src/xlsx/features.rs` | adapt | reading autofilters and CF into Grist filters and rules where they map |
| `crates/model/src/{cell,store,cellmap,sheet,workbook}.rs` | none | reject | A1 sparse store; our store is columnar |
| `crates/model/src/{macros,python,password,preserved,b64}.rs`, `features/pivot.rs`, `features/print.rs` | none | reject | Excel features |
| `crates/xlsx/src/{lib,package,xml,read,sheet_read,styles,theme,tables}.rs` | evaluate against calamine at M4 | adapt (conditional) | calamine 0.38 is the default; gridcraft's reader is the fallback if calamine's style/CF access is insufficient |
| `crates/xlsx/src/{write,sheet_write}.rs` | none | reject | `rust_xlsxwriter` 0.102 for export |
| `crates/xlsx/src/csv.rs` | `sheetbase-import/src/csv/sniff.rs` | adapt | encoding and delimiter sniffing; `csv` crate for parsing |
| `crates/xlsx/src/{cfb,crypto,xls,xlsb,ods}.rs` | none (v1) | reject | out of scope |
| `crates/xlsx/src/{chart,chartex,drawing,omml,pivot,richdata,controls,python_part,passthrough,feature_bags,array_formula,fmla}.rs` | none | reject | Excel object model |
| `crates/pdf/**` | none (v1) | reject | no PDF export; notices travel with it if ever harvested |
| `crates/math/**` | none | reject | LaTeX |
| `crates/chart/**` | none (v1; open question 8) | reject | `egui_plot` |
| `crates/engine/src/lib.rs` (Session, groups, panic guard), `cmd.rs` (CommandSpec) | `sheetbase-ui/src/commands/registry.rs`, `sheetbase-app/src/guard.rs` | adapt | command registry and catch_unwind pattern |
| `crates/engine/src/cmd/**` (78 files) | none | reject | Excel commands |
| `crates/engine/src/display.rs` | `sheetbase-ui/src/cells/format_cache.rs` | copy | format cache |
| `crates/engine/src/clip_html.rs` | `sheetbase-ui/src/grid/clipboard/html.rs` | copy, adapt | HTML clipboard read/write; add Grist's `data-grist-*` attributes |
| `crates/engine/src/selection.rs` | none | reject | xldatagrid's selection model is used |
| `crates/engine/src/fill.rs` | `sheetbase-ui/src/grid/fill.rs` | adapt (later) | drag-fill series beyond copy, post v1 |
| `crates/engine/src/io.rs` (`sniff`) | `sheetbase-import/src/sniff.rs` | adapt | content sniffing before trusting extensions |
| `crates/engine/src/{cf,tables,pivot*,paper,outline,macros,record,recent,stash,sample,links,windows,catalog,chart_svg}.rs` | none | reject | Excel features |
| `crates/mcp/**`, `apps/gridcraft/src/control_server.rs`, `ui-egui/src/control*.rs` | design reference for `sb serve` | adapt | JSON-RPC skeleton; our vocabulary |
| `crates/ui-egui/src/grid/geo.rs` | `sheetbase-ui/src/grid/geo.rs` | adapt | virtualised geometry with frozen panes; RTL kept as a feature flag |
| `crates/ui-egui/src/grid/quadrant.rs`, `cell_paint.rs` | `sheetbase-ui/src/grid/paint.rs` | adapt | paint order, overflow text, wrap, border dashes; galley cache added; per-cell `Style` clone removed |
| `crates/ui-egui/src/grid/show.rs` | `sheetbase-ui/src/grid/widget.rs` | adapt | scroll, zoom ladder, pane layout, custom scrollbar; page layout, outline, ink removed |
| `crates/ui-egui/src/grid/{interact,keyboard,selection,cursor,menus,tables}.rs`, `keymap.rs` | `sheetbase-ui/src/grid/{interact,drag}.rs` | adapt | `Drag` state machine, header resize/reorder, fill handle; keyboard replaced by xldatagrid's `decide()` |
| `crates/ui-egui/src/grid/editor.rs`, `editor.rs`, `formula_bar.rs` | `sheetbase-ui/src/grid/editor.rs` | adapt | in-cell editor sizing and `EditState`; point mode, Name Box, Python mode removed |
| `crates/ui-egui/src/selection_glide.rs` | `sheetbase-ui/src/grid/glide.rs` | copy | pure Rect animation |
| `crates/ui-egui/src/theme.rs`, `theme/tests.rs` (contrast part) | `sheetbase-ui/src/theme/mod.rs` | copy, re-skin | token struct, `contrast()`, WCAG test; our values |
| `crates/ui-egui/src/theme/{font_setup,font_fallback}.rs`, `fonts.rs` | `sheetbase-ui/src/theme/fonts.rs` | copy, adapt | system font discovery via skrifa; craft-fonts manifest removed |
| `crates/ui-egui/src/desktop_theme.rs` | `sheetbase-app/src/platform/linux_theme.rs` | copy | portal light/dark |
| `crates/ui-egui/src/icons.rs` | `sheetbase-ui/src/icons.rs` | copy selectively | the icons we need |
| `crates/ui-egui/src/code_editor.rs` | `sheetbase-ui/src/cells/formula_editor.rs` | copy, adapt | monospace editor with tokeniser hook; SFL tokeniser plugged in |
| `crates/ui-egui/src/widgets.rs` | none | reject | ribbon buttons |
| `crates/ui-egui/src/app/clipboard.rs`, `services.rs`, `app.rs` frame loop | `sheetbase-app/src/{clipboard,services,app}.rs` | adapt | host-injected clipboard closures, perf counters, interface scale |
| `crates/ui-egui/src/{ribbon/**, backstage*, dialogs/**, keytips/**, i18n/**, tabs, panes, paper_view, printing, outline, pivot_pane, chartview, objects, floating_pictures, cell_pictures, equation, macro_*, credits, craft_fonts_policy, updates_ui, doc_windows, form_controls, text_box, border_preview, function_library, formula_locale, dnd}.rs` | none (`doc_windows.rs` as reference for viewports) | reject | Excel chrome and suite integration |
| `crates/ui-egui/tests/it/*` | style reference | adapt | kittest patterns |
| `apps/gridcraft/src/{main,graphics,logging,native_menu,apple_events,print}.rs` | `sheetbase-app/src/platform/` | adapt | eframe/wgpu shell, adapter probe, native menus, Apple events; branding and updater removed |
| `apps/gridcraft-web/**` | none (v1) | reject | no web build |
| `apps/gridcraft-cli/**` | design reference | adapt | subcommand pattern over the registry |
| `xtask/src/layers.rs` | `xtask/src/layers.rs` | copy, adapt | layer table replaced |
| `xtask/src/*` (assets, parity, i18n-report, ico) | none | reject | their tooling |
| `docs/architecture.md`, `docs/decisions.md` | none | reference only | |

Totals: about 20k lines copied (numfmt, functions, value compat, date, display cache, HTML
clipboard, glide, theme, fonts, code editor, layers), about 10k adapted (grid geometry and
paint, interact, editor, command registry, sniffers, style and feature types), the remaining
~210k rejected.

[^gridcraft]: storytold/gridcraft main, audited 2026-11-08 (workspace 0.16.0, edition 2024, rust-version 1.95, MIT OR Apache-2.0)
