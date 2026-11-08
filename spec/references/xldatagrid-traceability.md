---
type: Reference
title: xldatagrid traceability table
description: Every xldatagrid component, behaviour module and extension mapped to a sheetbase crate and module with a status of port, merge-with-grist, or drop and the reason.
tags: [references, xldatagrid, traceability, ui]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: xdg-repo
    resource: /Users/rom/workspace/xldatagrid/xldatagrid
    title: xldatagrid monorepo (packages/core, viewmodel, react, extensions, import, richtext, mui, fluent), 0.6.0, MIT
---

Paths are relative to the xldatagrid repo; `RS` = `packages/react/src`, `CORE` =
`packages/core/src`, `VM` = `packages/viewmodel/src`, `EXT` = `packages/extensions/src`.[^xdg-repo]
Status: **port** (behaviour reproduced in Rust, tests ported), **merge** (folded into the Grist
equivalent, behaviour kept where the two agree, Grist wins on conflict), **drop** (not built,
reason given).

# Core model and state

| # | xldatagrid | sheetbase | Status | Reason / notes |
|---|---|---|---|---|
| 1 | `CORE/grid-model.ts` (Causl node families `grid:*`) | `sheetbase-core::view_model` + `sheetbase-graph` namespaces | merge | Grist's section/field model is the data; nodes become `model:/controller:/view:` |
| 2 | `CORE/selection.ts` | `sheetbase-ui::grid::selection` | port | reducers and `SelectionIndex` verbatim in Rust |
| 3 | `CORE/located-rows.ts` | `sheetbase-ui::grid::located` | port | REPLACE/TOGGLE/EXTEND on a `controller:` node |
| 4 | `CORE/checkbox-selection.ts` | `sheetbase-ui::grid::gutter::checkbox` | port | tri-state header |
| 5 | `CORE/editing.ts`, `edit-draft.ts` | `sheetbase-ui::grid::editor::state` | port | `EditingState` enum; draft shared with the formula field |
| 6 | `CORE/undo-redo.ts`, `types/deltas.ts` | `sheetbase-core::actions` | merge | Grist's inverse doc actions replace `GridDelta` |
| 7 | `CORE/apply-deltas.ts` | `UserAction::ApplyDocActions` | merge | all-or-nothing is the bundle |
| 8 | `CORE/grid-interaction-state.ts` (29 actions) | `sheetbase-ui::state::interaction` | port | |
| 9 | `CORE/virtualization.ts` | `sheetbase-ui::grid::geo` | merge | gridcraft `Geo` with xldatagrid's overscan 3/1 and 600-height LRU |
| 10 | `CORE/filtering.ts` (operators) | `sheetbase-core::view_model::filter` | merge | Grist filter spec (`included/excluded/min/max`) is stored; xdg operators map onto the column filter menu's conditions |
| 11 | `CORE/sorting` | Grist `sortColRefs` | merge | |
| 12 | `CORE/clipboard.ts`, `paste-options.ts` | `sheetbase-ui::grid::clipboard` | merge | Grist HTML flavour + xdg tiling/coercion |
| 13 | `CORE/commit-intents.ts` | commit `intent` strings | port | closed table of intents |
| 14 | `CORE/cell-types/*.descriptor.ts` (27) | `sheetbase-ui::cells::registry` | merge | capabilities kept; types folded per [cell types](../ui/cell-types.md) |
| 15 | `CORE/number-format.ts`, `excel-serial.ts`, `temporal-*.ts` | `numfmt` (harvested) + `jiff` | merge | |
| 16 | `CORE/expression-evaluator.ts` (`=expr` in numeric cells) | SFL | merge | `=` opens the formula editor instead |
| 17 | `CORE/query/*` (lazy loading, `SparseRowStore`) | none | drop | documents are local and fully loaded; no server paging in v1 |
| 18 | `CORE/search-index/*` | `sheetbase-ui::find` | merge | find bar over formatted text; no IndexedDB index |
| 19 | `CORE/wasm-boot.ts`, `engine-pin.ts` | `sheetbase-graph::CauslGraph` | merge | the engine is linked natively |
| 20 | `CORE/types/events.ts` (EventBus before/on/after) | `sheetbase-core::hooks` (`MetaHook`) + ACL pre-check | merge | vetoable `before:` becomes ACL and `TableLocked` checks |

# Viewmodel

| # | xldatagrid | sheetbase | Status | Reason |
|---|---|---|---|---|
| 21 | `VM/keyboard-controller.ts` `decide()` | `sheetbase-ui::grid::keyboard::decide` | port | with Grist bindings merged ([keyboard](../ui/keyboard.md)) |
| 22 | `VM/keyboard-intents.ts`, `input-intents.ts` | same | port | modifier meaning in one place |
| 23 | `VM/pointer-controller.ts`, `pointer-intents.ts` | `sheetbase-ui::grid::pointer` | port | |
| 24 | `VM/context-menu.ts` | `sheetbase-ui::menus::context` | merge | Grist menu items; xdg keyboard model and access keys |
| 25 | `VM/clipboard-limit.ts` | `clipboard::limit` | port | 300 MB cap |
| 26 | `VM/draft-state-controller.ts` | `editor::state` | port | |
| 27 | `VM/expression-draft-controller.ts` | none | drop | replaced by the formula editor |
| 28 | `VM/import/import-wizard-controller.ts` | `sheetbase-import::ImportPlan` + `sheetbase-ui::import::wizard` | merge | steps kept; conflict/key strategies kept; Grist's transform columns not used |
| 29 | `VM/clear-intent.ts` | `grid::commands::clear` | port | |

# React grid chrome

| # | xldatagrid | sheetbase | Status | Reason |
|---|---|---|---|---|
| 30 | `RS/DataGrid.tsx` (root, props) | `GridWidget` + `GridOptions` | merge | props become `SectionOptions` + `Prefs` |
| 31 | `RS/body/DataGridBody.tsx` | `grid::paint` | merge | egui painter; DOM virtualisation gone |
| 32 | `RS/body/body-cell-render.tsx`, `cell-editors.tsx`, `cell-text-display.tsx`, `cell-truncation.ts` | `cells::render`, `cells::editor` | port | overflow policies kept (truncate end/middle, clamp 2/3 lines, wrap) |
| 33 | `RS/body/commit-advance.ts` | `grid::commit_advance` | port | Shift+Tab inconsistency settled: always moves |
| 34 | `RS/body/drag-select.ts` | `grid::drag_select` | port | incl. edge auto-scroll |
| 35 | `RS/body/FillHandle.tsx` (inert) | `grid::fill_handle` | merge | we implement drag-fill (copy) which xdg did not |
| 36 | `RS/body/row-overlays.tsx` | `grid::paint::overlays` | port | |
| 37 | `RS/body/DataGridFooterRow.tsx` (aggregates) | none in grid | drop | Grist has no footer row; summary tables are the aggregate story; status bar shows selection sums |
| 38 | `RS/body/DataGridTitlesRow.tsx` (titles as first row) | none | drop | Excel-worksheet skin feature |
| 39 | `RS/body/use-gutter-row-ops.ts` | `grid::gutter` | merge | Grist row menu |
| 40 | `RS/body/focus-fallback.ts`, `use-pending-lazy-focus.ts` | none | drop | DOM focus keepalive; egui focus is ours |
| 41 | `RS/body/natural-cell-height.ts` | `geo::measure` | port | measured heights with LRU |
| 42 | `RS/body/unique-draft-check.ts` | none | drop | no unique-column constraint in Grist; a `#DUPLICATE` rule can be a conditional format |
| 43 | `RS/GhostRow.tsx` + `ghost-*.ts` | `grid::new_row` | merge | Grist new-row line with xdg draft semantics; `saveControl` buttons dropped |
| 44 | `RS/header/DataGridHeader.tsx` | `grid::header` | merge | sort badges, funnel, kebab, drag reorder, resize, autofit kept |
| 45 | `RS/header/DataGridColumnMenu.tsx` | `grid::menus::column` | merge | Grist column menu items |
| 46 | `RS/header/column-filter-menu/*` | `filters::menu` | port | Excel-365 style filter menu with savepoint |
| 47 | `RS/header/FilterConditionDialog.tsx` | `filters::condition` | port | |
| 48 | `RS/header/DataGridColumnChooser.tsx` | `fields::chooser` | port | |
| 49 | `RS/header/DataGridColumnSettingsDialog.tsx` (unique) | none | drop | see 42 |
| 50 | `RS/header/DataGridColumnGroupHeader.tsx` | none | drop | Grist has no column groups |
| 51 | `RS/header/LettersRow.tsx`, `LettersCell.tsx`, headings band | none | drop | A1 letters are an Excel-skin feature |
| 52 | `RS/chrome/ChromeRowNumberCell.tsx`, `chrome-item-strip.tsx` | `grid::gutter` | merge | row numbers, select-all corner, row menu; item strip composability dropped |
| 53 | `RS/chrome/ChromeControlsCell.tsx` (per-row action buttons) | none | drop | no host-defined row actions in a document app |
| 54 | `RS/chrome/ChromeCheckboxCell.tsx` | `grid::gutter::checkbox` | port | optional checkbox gutter for multi-row ops |
| 55 | `RS/MasterDetail.tsx` | Grist card section linked by cursor | merge | |
| 56 | `RS/TransposedGrid.tsx` | Grist card view | merge | |
| 57 | `RS/regions/*`, `slots/*` (Toolbar, FormulaBar, StatusBar, EmptyState, SheetTabs) | `shell`, `status`, `pages` | merge | SheetTabs become the page tree; FormulaBar is an open question |
| 58 | `RS/toolbar/DataGridToolbar.tsx` | section frame menu | merge | |
| 59 | `RS/ContextMenu.tsx` + placement | `menus::context` | port | |
| 60 | `RS/HoverTooltip.tsx`, `ValidationTooltip*.tsx`, `ValidationSummary.tsx` | `tooltip`, error navigation (F8) | merge | validation becomes cell errors |
| 61 | `RS/use-row-drag-drop.ts`, `drag-preview.ts` | `grid::drag` | port | |
| 62 | `RS/use-drag-drop.ts`, `EXT/drop-to-attach` | none | drop | attachments are read-only in v1 |
| 63 | `RS/locate-scope.tsx` | `grid::located` | port | |
| 64 | `RS/column-autocomplete/*` | `cells::editor::autocomplete` | port | Excel-style inline completion from column values |
| 65 | `RS/color/*` | `pickers::color` | merge | palette picker only |
| 66 | `RS/clipboard/*` | `clipboard` | port | limit dialog |
| 67 | `RS/render-extensions/*` | none | drop | React decoration seam; conditional formatting covers styling |
| 68 | `RS/import/ImportWizard.tsx` + steps | `import::wizard` | port | |
| 69 | `RS/strings/*` (i18n) | `sheetbase-ui::strings` | merge | English only in v1, string table kept for later |
| 70 | `RS/identity/*` | `User` | merge | |
| 71 | `RS/a11y/GridLiveRegion.tsx`, announcer | `a11y::Announcer` (AccessKit live node) | merge | |
| 72 | `RS/styles/*` (CSS layers, 186 tokens, surfaces) | `theme::Tokens` | merge | token *idea* kept; CSS gone |
| 73 | `RS/theme/*` bridges | none | drop | no host theme bridge |

# Cells

| # | xldatagrid | sheetbase | Status | Reason |
|---|---|---|---|---|
| 74 | text, numeric, currency, boolean, booleanSelected, calendar, status, list, dropdown, chipSelect, tags, compoundChipList, password | see [cell types](../ui/cell-types.md) | merge | each maps onto a Grist type x widget |
| 75 | richText (TipTap composer, MarkdownView) | Markdown widget render; plain text edit | merge | WYSIWYG composer dropped (TipTap is DOM) |
| 76 | rating, iconRating, slider | Numeric Spinner variants (`slider` option) | merge | rating stars as a Numeric widget option; iconRating dropped |
| 77 | range, numericRange, ordinalChips, measurement | none | drop | no Grist type; a Text column with a formula covers them |
| 78 | passwordConfirm | none | drop | form feature, not a document cell |
| 79 | upload, fileAttachment (+ PreviewPane, viewer registry) | Attachments widget (viewer only) | merge | |
| 80 | actions | none | drop | see 53 |
| 81 | subGrid (nested DataGrid) | linked sections | merge | Grist's model for nested data |
| 82 | detailTrigger | card view link | merge | |
| 83 | `cells/CellPopover`, `DropdownFoundation`, primitives | `cells::popup` | port | anchored popup with flip; drag-resize dropped |

# Extensions and skins

| # | xldatagrid | sheetbase | Status | Reason |
|---|---|---|---|---|
| 84 | `EXT/createValidation`, `createRegexValidation` | conditional formatting + trigger formulas | merge | |
| 85 | `EXT/createExportExtension` (csv/tsv/xml/xlsx/xls/pdf) | `sheetbase-import` export (csv/tsv/xlsx) | merge | xml, xls, pdf dropped |
| 86 | `EXT/createFormulaBar`, `useNameBox` | open question 5 | drop (v1) | |
| 87 | `EXT/createExcelMode` | none | drop | Excel skin |
| 88 | `EXT/createColumnAutoComplete` | 64 | port | |
| 89 | `EXT/createUniqueColumns` | none | drop | see 42 |
| 90 | `EXT/createColumnResize` | header resize | port | |
| 91 | `EXT/createCellComments` | `_grist_Cells` read-only | merge | |
| 92 | `EXT/createArithmeticExpressions` | SFL | merge | |
| 93 | `EXT/createAttachmentRevisions` | none | drop | no revision model in Grist attachments |
| 94 | `EXT/createModelBridge` | `sb serve` | merge | |
| 95 | `packages/mui`, `packages/fluent` skins | none | drop | DOM component libraries |
| 96 | `packages/import` adapters (csv, xlsx, xls, xml), worker | `sheetbase-import` (csv, xlsx) | merge | xls/xml dropped for v1 |
| 97 | `packages/richtext` | Markdown render (`pulldown-cmark`) | merge | |
| 98 | Storybook stories, Playwright specs, fast-check properties | kittest cases, proptests | port (as a checklist) | names recorded in test comments |
| 99 | pre-commit gates (`no-behaviour-in-skins`, `no-modifier-decisions`, file-size budget) | `cargo xtask ci` lints | merge | `no-modifier-decisions` becomes a clippy-lint-style test that only `keyboard::mods` reads `Modifiers` |

[^xdg-repo]: xldatagrid monorepo (packages/core, viewmodel, react, extensions, import, richtext, mui, fluent), 0.6.0, MIT
