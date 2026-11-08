# Component Design

* [Accessibility](a11y.md) - What egui plus AccessKit can deliver and what we commit to: roles and properties for the grid tree, the announcer, focus order, reduced motion, high contrast, and the gaps egui leaves.
* [UI architecture](architecture.md) - How sheetbase-ui and sheetbase-app are put together: the eframe frame loop, the AppState, the command registry, the view store fed by Causl view nodes, and the rule that the UI only ever calls user actions.
* [Grid widget](grid.md) - The grid: geometry and virtualisation (gridcraft Geo adapted), the paint pipeline, headers and gutter, frozen columns, the new-row line, column and row drag, resize, fill handle, context menus, in-cell editor, clipboard; with the xldatagrid behaviours folded in.
* [UI performance](performance.md) - The 60 fps budget for the grid and how it is met: visible-window painting, the galley cache keyed by node version, incremental row lists, memoisation rules, and the measured gates.
* [Selection state machine](selection.md) - The grid selection as an explicit finite state machine over xldatagrid's SelectionState and reducers, with the Grist cursor as the active range's anchor, multi-range support, and the drag and keyboard transitions.
* [Theming](theming.md) - The token set in light and dark, with every key text/background pair's WCAG ratio measured (4.5:1 normal text, 3:1 UI), the contrast test that gates it, and how Grist's per-cell colours and the user's preferences compose.

# Overview

* [About the UI section](_about.md) - The egui front end: architecture, the grid widget, keyboard model, selection state machine, cell types and editors, the full widget catalogue, accessibility, theming with measured contrast, and the 60 fps performance plan.

# Reference

* [Cell types, renderers and editors](cell-types.md) - Grist's column type x widget matrix as the cell-type registry, each with its renderer, editor, capabilities (type-to-edit, Space behaviour, commit advance) and the xldatagrid cell types that fold into it.
* [Keyboard model](keyboard.md) - Every key binding of v1, merged from Grist's commandList and xldatagrid's keyboard controller, with the decide() contract that makes them testable without a window.
* [Widget catalogue](widgets.md) - Every egui widget sheetbase-ui provides outside the grid: pages, sections, card views, chart, creator panel, filter and sort UI, find, import wizard, access rules page, history, status bar, dialogs; each with its data source, commands emitted and test.
