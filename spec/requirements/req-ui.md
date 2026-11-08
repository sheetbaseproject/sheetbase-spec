---
type: Requirement
title: "Requirements: UI, accessibility and UI performance"
description: "REQ-UI, REQ-A11Y and REQ-PERF (UI part): the grid and widget catalogue, keyboard model, selection, clipboard, theming with measured contrast, AccessKit tree, 60 fps budget."
tags: [requirements, ui, a11y, performance]
status: draft
requirement_id: REQ-UI/REQ-A11Y/REQ-PERF
priority: must
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

| Id | Requirement | Priority | Verification |
|---|---|---|---|
| REQ-UI-01 | Every row of the [xldatagrid traceability table](../references/xldatagrid-traceability.md) marked port or merge has a corresponding module and test. | must | table-to-code audit at M5/M6 (`xtask trace xldatagrid`) |
| REQ-UI-02 | Every binding in [keyboard](../ui/keyboard.md) works and `decide()` is pure and unit-tested. | must | keyboard test table |
| REQ-UI-03 | The selection FSM in [selection](../ui/selection.md) is implemented over the ported reducers and proptested. | must | FSM proptest |
| REQ-UI-04 | Copy produces Grist's HTML clipboard flavour plus TSV; paste from Grist keeps raw values; paste tiles over the selection and extends rows. | must | clipboard fixtures |
| REQ-UI-05 | Every widget in [the catalogue](../ui/widgets.md) exists with a kittest module and snapshots in both themes at 1x. | must | catalogue audit |
| REQ-UI-06 | Every cell type x widget in [cell types](../ui/cell-types.md) renders and edits per its capabilities. | must | per-type kittest |
| REQ-UI-07 | Light and dark themes meet WCAG AA for every pair in [theming](../ui/theming.md) and the test fails on regression. | must | `every_pair_meets_wcag_in_both_themes` |
| REQ-UI-08 | HiDPI: geometry is point-based and pixel-snapped; snapshots at ppp 1.0 and 2.0 are both crisp (no blurred 1 px lines). | must | snapshot review |
| REQ-UI-09 | Interface scale 75 to 200 percent and reduced motion are honoured everywhere. | should | kittest at 3 scales |
| REQ-UI-10 | Column resize, reorder, freeze, row drag, fill-handle copy, find, context menus and the new-row line behave as specified in [grid](../ui/grid.md). | must | grid kittest catalogue |
| REQ-A11Y-01 | The visible grid exposes an AccessKit tree with `Grid`/`Row`/`Cell`/`ColumnHeader`/`RowHeader` roles, indices, selection and sort state, and the focused cell. | must | `tests/a11y_grid.rs` |
| REQ-A11Y-02 | An announcer node delivers the events listed in [a11y](../ui/a11y.md); every dialog traps focus and restores it. | must | kittest queries |
| REQ-A11Y-03 | A VoiceOver and an NVDA walkthrough of open, navigate, edit, undo, filter, link is recorded before 1.0. | should | M7 checklist |
| REQ-PERF-04 | `grid_paint_900` under 6 ms p95; `grid_scroll_100k` under 9 ms p95 with galley cache hit rate over 85 percent. | must | bench gate |
| REQ-PERF-05 | `grid_edit_latency` (keystroke to paint, 5 dependent columns over 100k rows) under 30 ms. | must | bench gate |
| REQ-PERF-06 | Idle frames are not painted; CPU at idle under 1 percent. | should | manual measurement + a test that counts repaint requests |
