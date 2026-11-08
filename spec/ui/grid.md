---
type: Component Design
title: Grid widget
description: "The grid: geometry and virtualisation (gridcraft Geo adapted), the paint pipeline, headers and gutter, frozen columns, the new-row line, column and row drag, resize, fill handle, context menus, in-cell editor, clipboard; with the xldatagrid behaviours folded in."
tags: [ui, grid, egui]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: gridcraft-geo
    resource: https://github.com/storytold/gridcraft/blob/main/crates/ui-egui/src/grid/geo.rs
    title: gridcraft grid/geo.rs (Geo, LineIndex, frozen panes, hit testing)
  - id: gridcraft-quadrant
    resource: https://github.com/storytold/gridcraft/blob/main/crates/ui-egui/src/grid/quadrant.rs
    title: gridcraft grid/quadrant.rs (paint order)
  - id: grist-gridview
    resource: https://github.com/gristlabs/grist-core/blob/main/app/client/components/GridView.js
    title: GridView.js (paste tiling, fillSelectionDown, column/row drag, freeze)
---

# Public API

```rust
pub struct GridWidget<'a> {
    pub section: RowId,                         // _grist_Views_section id
    pub view: &'a DocView<'a>,
    pub state: &'a mut GridUiState,             // scroll, selection, editor, drags, hover, caches
    pub theme: &'a Theme,
    pub options: GridOptions,                   // from SectionOptions + Prefs: gridlines, zebra, row numbers, numFrozen, rowHeight
}
impl<'a> GridWidget<'a> {
    pub fn show(self, ui: &mut egui::Ui) -> GridResponse;     // paints, handles input, returns commands + a11y updates
}
pub struct GridResponse { pub commands: Vec<Command>, pub focused: bool, pub cursor_cell: Option<CellAddr>, pub visible: VisibleRange }
```

# Geometry and virtualisation (gridcraft `Geo` adapted)[^gridcraft-geo]

```rust
pub struct Geo {
    pub rect: Rect, pub scroll: Vec2, pub zoom: f32 /* interface scale x pixels_per_point */,
    pub header_h: f32 /* 24 pt */, pub gutter_w: f32 /* 40 pt row numbers, 0 if off */,
    pub rows: LineIndex /* prefix sums over row heights; uniform fast path when rowHeightUniform */,
    pub cols: LineIndex /* prefix sums over field widths */,
    pub frozen_cols: u32, pub frozen_w: f32,
}
impl Geo {
    pub fn visible_rows(&self) -> Range<usize>;              // + 3 rows overscan each side (xldatagrid), clamped
    pub fn visible_cols(&self) -> Range<usize>;              // + 1 col overscan
    pub fn cell_rect(&self, row: usize, col: usize) -> Rect; // snapped to half-points for crisp 1 px lines at integer ppp
    pub fn cell_at(&self, pos: Pos2) -> Option<CellHit>;     // Header(col) | Gutter(row) | Corner | Cell(row, col) | NewRow(col) | FrozenEdge
}
```

Row heights: `rowHeight` from section options (default 1 line = 24 pt, Grist's compact), or
measured when `rowHeightUniform = false` (wrapping text), with an LRU of 600 measured heights
that never evicts a visible row (xldatagrid constant). Column widths from
`_grist_Views_section_field.width` (default 100 px like Grist's `defaultWidth`), min 20, max 4096.

# Paint pipeline (one quadrant call per pane: frozen/unfrozen x header/body)[^gridcraft-quadrant]

1. Background and zebra stripes.
2. Gridlines (1 px, snapped).
3. Cell backgrounds (conditional `fillColor`, selected range tint, cursor row highlight).
4. Cell contents via the cell renderer registry ([cell types](cell-types.md)); galleys from the
   `GalleyCache` keyed by `(column node version, row id, field width, style hash, zoom)`.
5. Selection: range fill and perimeter (`SelectionIndex::borders`), cursor outline 2 px in
   `accent`, fill handle 6 x 6 pt square at the cursor's bottom right.
6. Error and censored markers (`#...` red short code; `Censored` as a hatched cell).
7. Drag overlays: column shadow, row shadow, drop indicator line.
8. Headers: labels, sort arrow with priority badge for multi-sort, filter funnel, column menu
   kebab on hover, resize handle 5 pt hit zone, frozen edge handle.
9. Gutter: row numbers (or `manualSort` position in raw view), row menu on hover, new-row `+`.
10. In-cell editor on top (an egui `TextEdit` sized to the cell, grows right then down).

# Interaction (drag state machine, gridcraft `Drag` adapted)

```rust
pub enum Drag {
    None,
    Select { anchor: CellAddr, additive: bool, last: Option<CellAddr> },      // xldatagrid drag-select, edge auto-scroll 2..18 pt/frame
    Rows { ids: Vec<RowId>, target: Option<(usize, Half)> },                   // Grist moveRows -> manualSort updates
    Cols { fields: Vec<RowId>, target: Option<usize> },                        // Grist moveColumns -> parentPos updates
    ResizeCol { field: RowId, start_x: f32, orig: f32 },                      // commit on release: UpdateRecord _grist_Views_section_field.width
    ResizeRow { start_y: f32, orig: f32 },                                    // section rowHeight option
    Freeze { col: u32 },                                                      // numFrozen on release
    Fill { from: CellRange, to: CellRange },                                  // fill handle: fillSelectionDown semantics extended to drag (series: copy only, v1)
}
```

Double-click on a column edge autofits (measure visible galleys + 8 pt). Double-click on the
row-number edge resets row height.

# Clipboard

Copy writes `text/plain` TSV of formatted values and `text/html` with Grist's exact table
markup (`<table border=1 cellspacing=0 style="white-space: pre" data-grist-doc-id-hash=...>`,
`<col data-grist-col-ref data-grist-col-type>`, `<td data-grist-raw-value='JSON'>`), so paste into
Grist and from Grist keeps raw values when types are compatible. Paste prefers HTML, tiles the
block over the selection (rounded down to whole multiples), extends rows (`BulkAddRecord` with
`null` ids) but never columns, uses raw values when the doc hash matches or types match, else
parses text per column type (xldatagrid `coercePastedCell` + Grist `parsePasteForView`).[^grist-gridview]
Cut is copy followed by clear in one `linkId` chain. A 300 MB copy limit shows the limit dialog.

# New row

The last line is Grist's "add row" line (xldatagrid's ghost row semantics): typing or pasting
there creates the record with link `default_values` applied; `Enter` on it adds and moves down;
`Esc` discards the draft.

# Context menus

Cell: Cut, Copy, Paste, Paste values | Insert row above/below, Duplicate rows, Delete rows |
Insert column left/right, Rename, Hide, Delete column | Filter by this value, Clear filter |
Sort A to Z, Z to A | Copy link to cell | View as card. Header: Sort, Add to sort, Freeze to
here, Hide, Column options, Delete. Gutter: row items. Built from the command registry.

# Tests

`egui_kittest` harness per behaviour (click, drag, keys), snapshot tests for painting at
1.0 and 2.0 ppp in both themes, and the xldatagrid Playwright catalogue ported as named cases
(`grid-keyboard`, `edit-commit-nav`, `type-to-edit`, `clipboard-copy`, `row-drop-indicator`,
`column-drop-indicator`, `cell-overflow`, `hover-tooltip`, `row-select-styling`).

[^gridcraft-geo]: gridcraft grid/geo.rs (Geo, LineIndex, frozen panes, hit testing)
[^gridcraft-quadrant]: gridcraft grid/quadrant.rs (paint order)
[^grist-gridview]: GridView.js (paste tiling, fillSelectionDown, column/row drag, freeze)
