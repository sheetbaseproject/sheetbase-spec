---
type: Decision
title: "ADR-011: The grid ports xldatagrid's pure decision layers onto egui, and merges them with Grist's view model"
description: Selection reducers, the keyboard decide() function, the pointer decision layer, the commit pipeline and the interaction reducer from xldatagrid are ported as pure Rust modules; DOM-specific pieces (ARIA attributes, CSS layers, portals, skins) are replaced by AccessKit, egui styles and egui popups; Grist's section/field model is the data these layers operate on.
tags: [decision, ui, grid, xldatagrid]
status: draft
decision_id: ADR-011
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: xdg-keyboard
    resource: /Users/rom/workspace/xldatagrid/xldatagrid/packages/viewmodel/src/keyboard-controller.ts
    title: xldatagrid keyboard-controller.ts (pure decide(), 1499 lines)
  - id: xdg-selection
    resource: /Users/rom/workspace/xldatagrid/xldatagrid/packages/core/src/selection.ts
    title: xldatagrid selection.ts (SelectionState, pure reducers, buildSelectionIndex)
  - id: xdg-model
    resource: /Users/rom/workspace/xldatagrid/xldatagrid/packages/core/src/grid-model.ts
    title: xldatagrid grid-model.ts (Causl node families, setCellValue chokepoint)
---

# Context

xldatagrid is a React/DOM grid whose behaviour is concentrated in framework-free layers: a
`SelectionState` with pure reducers,[^xdg-selection] a keyboard controller whose `decide()`
maps a key event plus a model snapshot to an intent,[^xdg-keyboard] a pointer decision layer, a
single `setCellValue` commit chokepoint with validation and vetoable events,[^xdg-model] and a
`GridInteractionState` reducer for menus, drags and resizes. Its rendering, a11y and theming are
DOM: ARIA roles, `aria-rowindex`, one live region, CSS cascade layers with 186 tokens, portals.

The brief had assumed a `controller:gridSelection` statechart and `model:/controller:/view:`
namespaces; neither exists in xldatagrid (all nodes are `grid:*`). The port adopts the
namespaces anyway, because Causl's guidance asks for them and because Grist's view model
(sections, fields, cursors, link filters) gives them real content.

# Decision

- **Port as pure Rust, test first**: `sheetbase-ui::grid::selection` (reducers and
  `SelectionIndex`), `::keyboard` (`decide(&KeyEvent, &GridSnapshot) -> Decision`), `::pointer`
  (`decide_cell_press`, `decide_row_press`), `::interaction` (the reducer with its 29 actions),
  `::commit_advance`, `::drag_select` (with edge auto-scroll), `::clipboard` (TSV + HTML,
  tiling paste), `::ghost_row`. Each module's TypeScript test cases become Rust tests before any
  painting exists.
- **Replace, not port**: ARIA attributes become AccessKit node properties (`Role::Grid`,
  `Role::Row`, `Role::Cell`, `row_index`, `column_index`, `selected`, `sort_direction`,
  `live` on an announcer node); the live region becomes `sheetbase-ui::a11y::Announcer` pushing
  `Live::Polite` updates; CSS tokens become a `Theme` struct of `Color32` tokens with a WCAG
  contrast test (gridcraft's pattern); portals become egui `Area`/`Popup`; skins (MUI, Fluent)
  are dropped with reason.
- **Merge with Grist**: xldatagrid's `ColumnDef` becomes Grist's `ViewField` + `Column`;
  its 27 cell types collapse onto Grist's column types and widgets (mapping in
  [cell types](../ui/cell-types.md)); its ghost row is Grist's "new row" line at the bottom of a
  grid; its chrome columns (row numbers, checkbox, controls) become the grid gutter with Grist's
  row-number behaviours; its filter menu is Grist's column filter; sub-grids, master-detail,
  transposed grid and the import wizard map onto Grist's linked sections, card view and import
  flow respectively.
- **Traceability**: every xldatagrid component has a row in
  [the traceability table](../references/xldatagrid-traceability.md) with one of `port`,
  `merge-with-grist`, `drop` and a reason.

# Alternatives

**Port the whole React grid structure (components one to one).** Rejected: half of it is DOM
plumbing (virtualisation via absolute divs, sticky columns, ResizeObserver, portals, CSS
layers) that egui does differently or not at all.

**Start from gridcraft's grid and bolt on relational features.** Its `Geo`, quadrant painter
and interaction state machine are mature and are harvested. But its selection is Excel ranges
over an infinite sheet, its keyboard model is Excel's, and its a11y is thin. The decision layers
of xldatagrid are the better behavioural source; gridcraft is the better painting source. We use
both where each is strongest.

# Consequences

- Behaviour fidelity is testable without pixels: the 739 Playwright specs of xldatagrid are a
  catalogue of cases; the ones about pure behaviour port as unit tests, the visual ones as
  `egui_kittest` snapshots.
- Two inconsistencies in xldatagrid are settled for the port: Shift+Tab always moves back (the
  custom-renderer "commit in place" behaviour is dropped); PgUp/PgDn move the cursor a page
  (Grist's `pageDown`/`pageUp` commands), not just seed a cold grid.

[^xdg-keyboard]: xldatagrid keyboard-controller.ts (pure decide(), 1499 lines)
[^xdg-selection]: xldatagrid selection.ts (SelectionState, pure reducers, buildSelectionIndex)
[^xdg-model]: xldatagrid grid-model.ts (Causl node families, setCellValue chokepoint)
