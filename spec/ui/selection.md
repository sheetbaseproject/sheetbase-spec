---
type: Component Design
title: Selection state machine
description: The grid selection as an explicit finite state machine over xldatagrid's SelectionState and reducers, with the Grist cursor as the active range's anchor, multi-range support, and the drag and keyboard transitions.
tags: [ui, grid, selection, fsm]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: xdg-selection
    resource: /Users/rom/workspace/xldatagrid/xldatagrid/packages/core/src/selection.ts
    title: xldatagrid selection.ts (SelectionState, reducers, buildSelectionIndex)
  - id: xdg-pointer
    resource: /Users/rom/workspace/xldatagrid/xldatagrid/packages/viewmodel/src/pointer-controller.ts
    title: xldatagrid pointer-controller.ts (decideCellPress, decideRowPress)
---

# Data (xldatagrid, ported)[^xdg-selection]

```rust
pub struct CellAddr { pub row: RowId, pub field: RowId }          // by id, never by index
pub struct CellRange { pub anchor: CellAddr, pub focus: CellAddr, pub kind: RangeKind }   // RangeKind: Cells | Row | Column
pub struct SelectionState { pub mode: SelectionMode /* Cell | Row | Range | None */, pub ranges: Vec<CellRange> }   // last range is active
pub struct SelectionIndex { /* normalised boxes against the current row list and field list; unresolvable endpoints drop the range */ }
impl SelectionIndex {
    pub fn build(sel: &SelectionState, rows: &[RowId], fields: &[RowId]) -> Self;
    pub fn contains(&self, row: usize, col: usize) -> bool;
    pub fn borders(&self, row: usize, col: usize) -> Borders;    // for the perimeter paint
    pub fn active(&self) -> Option<Box2>;
}
```

The Grist cursor (`controller:section:{id}:cursor`) is the active range's **anchor**; the
painted focus cell is its **focus** (xldatagrid's convention). `onSelectionChange`-style
consumers (copy, fill, linking) read the active range.

Reducers (pure, tested from the TypeScript cases): `select_cell`, `add_cell_selection`,
`extend_selection`, `select_row`, `extend_row_selection`, `toggle_row_selection`,
`select_column`, `select_all`, `clear_selection`, `is_single_cell`.

# States

```
                 +-----------+   press cell / arrow        +---------------+
   (no doc) ---->|   Cold    |---------------------------->|  CellActive   |<--------------------------+
                 +-----------+                             +---------------+                           |
                                                            |   |   |   |  ^                           |
              Shift+arrow / Shift+press / drag enters 2nd cell  |   |   |  | Esc (range -> cell)      |
                                                            v   |   |   |  |                           |
                                                      +-------------+ |   |  +----------------+       |
                                                      | RangeActive |-+   |  |  RowSelected   |       |
                                                      +-------------+     |  +----------------+       |
                                                            |             |      ^ gutter press /     |
                                      additive drag (Ctrl held at press) |      | Shift+Space        |
                                                            v             |      |                    |
                                                      +--------------+    |  +----------------+      |
                                                      | MultiRange   |    +->| ColumnSelected |      |
                                                      +--------------+       +----------------+      |
                                                                                                     |
   Enter / F2 / type / dblclick from CellActive  ---------------------->  +---------+  commit/cancel -+
                                                                           | Editing |
                                                                           +---------+
   Tab/Shift+Tab into a widget cell (Attachments, actions) ------------->  +-------------+  Esc / Tab out
                                                                           | WidgetFocus |
                                                                           +-------------+
```

| State | Invariant | Events handled |
|---|---|---|
| `Cold` | `ranges` empty, no cursor | any navigation key selects the first visible cell; press selects pressed cell |
| `CellActive` | one range, anchor == focus, kind Cells | arrows move; Shift+arrow -> `RangeActive`; press elsewhere re-selects; re-press on the same sole cell with `deselect_on_reclick` -> `Cold`; Enter/F2/type -> `Editing`; gutter press -> `RowSelected`; header press -> `ColumnSelected`; Mod+A -> `RangeActive` (all) |
| `RangeActive` | one range, anchor != focus | Shift+arrow/press moves focus; arrow collapses to a single cell at focus+delta; Esc -> `CellActive` at anchor; drag updates focus; Ctrl+press on another cell -> `MultiRange` |
| `MultiRange` | >1 ranges, last active | Ctrl+press/drag appends; Shift+arrow extends active; Esc -> `RangeActive` keeping only the active range (one level per press); plain press -> `CellActive` |
| `RowSelected` | ranges of kind Row | Shift+gutter extends; Ctrl+gutter toggles; Up/Down move the row selection; Left/Right swallowed; Esc -> `CellActive` at the anchor cell |
| `ColumnSelected` | kind Column | Shift+header extends; Ctrl+header adds; Esc -> `CellActive` |
| `Editing` | an editor owns input; selection frozen | commit (Enter/Tab/blur inside grid) -> `CellActive` at the advance target; cancel (Esc) -> `CellActive`; a press on another cell commits then selects (xdg `commit-on-grid-pointer`) |
| `WidgetFocus` | focus is inside a cell's own controls | Tab cycles controls, exits at ends to next/prev cell; Esc returns to `CellActive` |

Guards: `mode == None` makes every selection reducer a no-op except `clear`; `ReadOnly` blocks
`Editing` entry (Enter moves down instead); the new-row line can only hold a single cell
selection (leaving it with Shift+arrow collapses to a plain select).

# Pointer decisions (xldatagrid `pointer-controller`, ported)[^xdg-pointer]

```rust
pub fn decide_cell_press(p: &Press, sel: &SelectionState, opts: &PressOptions) -> PressIntent;   // ExtendTo | ClearSelection | Select
pub fn decide_row_press(p: &Press, sel: &SelectionState) -> RowPressIntent;                     // ToggleRow | ExtendRowTo | SelectRow
```

Drag: arms only for the primary button without Shift, in `Cell`/`Range` mode, not while
editing; the first enter of another cell starts `begin_range` (additive if Ctrl at press);
later enters `extend_to`; return to the anchor is ignored; release ends; a drag that ended on
its anchor vetoes the click. Edge auto-scroll: margin `min(24 pt, inner/2)`, step 2 to 18
pt/frame ramping with overshoot.

# Linking

A `controller:section:{id}:cursor` write happens on every anchor change, with an incrementing
`edit` sequence, so `view:section:{target}:linkfilter` recomputes in the same commit and cursor
cycles resolve to the most recent edit, as Grist's `LinkingState` does.

# Tests

Proptest: for random sequences of reducer calls, `SelectionIndex::build` never panics, every
range's endpoints resolve or the range is dropped, `active()` is the last range, and the FSM
state derived from `SelectionState` matches the state the transition table predicts (the
`range-extend.property` and `getEndJumpCell.property` fast-check suites from xldatagrid port
directly).

[^xdg-selection]: xldatagrid selection.ts (SelectionState, reducers, buildSelectionIndex)
[^xdg-pointer]: xldatagrid pointer-controller.ts (decideCellPress, decideRowPress)
