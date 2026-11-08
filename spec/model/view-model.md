---
type: Component Design
title: View model
description: "Pages, views, sections, fields, sort and filter specs, linking, widget options, card layouts and conditional formatting, all derived as Causl view: nodes from model: data and controller: inputs."
tags: [model, views, linking]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-linking
    resource: https://github.com/gristlabs/grist-core/blob/main/app/client/components/LinkingState.ts
    title: LinkingState.ts (link types, filter output, cursor propagation)
  - id: grist-sortspec
    resource: https://github.com/gristlabs/grist-core/blob/main/app/common/SortSpec.ts
    title: SortSpec.ts and FilterState.ts (sortColRefs and filter JSON)
  - id: grist-boxspec
    resource: https://github.com/gristlabs/grist-core/blob/main/app/common/BoxSpec.ts
    title: BoxSpec.ts (layoutSpec)
---

# Records

```rust
pub struct SectionRec {
    pub id: RowId, pub table_ref: RowId, pub parent_id: RowId /* view */, pub kind: SectionKind,
    pub title: SmolStr, pub description: SmolStr, pub options: SectionOptions, pub chart_type: ChartType,
    pub layout_spec: Option<BoxSpec>, pub sort: Vec<SortSpec>, pub link: Option<LinkSpec>,
    pub rules: Vec<RowId>, pub fields: Vec<RowId> /* parentPos order */,
}
pub enum SectionKind { Record, Detail, Single, Chart, Custom, Form }      // parentKey values
pub struct LinkSpec { pub src_section: RowId, pub src_col: Option<RowId>, pub tgt_col: Option<RowId> }
pub struct SectionOptions {                      // _grist_Views_section.options JSON
    pub vertical_gridlines: bool, pub horizontal_gridlines: bool, pub zebra_stripes: bool, pub row_numbers: bool,
    pub num_frozen: u32, pub row_height: Option<u32>, pub row_height_uniform: bool,
    pub chart: ChartOptions,                     // multiseries, lineConnectGaps, lineMarkers, stacked, invertYAxis, logYAxis, errorBars, donutHoleSize, showTotal, textSize, isXAxisUndefined, orientation, aggregate
    pub rules_options: Vec<Style>, pub custom_view: Option<serde_json::Value>, pub extra: serde_json::Map, // unknown keys preserved
}
pub struct FieldRec { pub id: RowId, pub section: RowId, pub col_ref: RowId, pub width: u32, pub widget_options: WidgetOptions, pub display_col: Option<RowId>, pub visible_col: Option<RowId>, pub rules: Vec<RowId> }
```

Sort spec: JSON array of `ColSpec` = `i64` (negative for descending) or
`"-12:emptyLast;naturalSort;orderByChoice;emptyFirst"`.[^grist-sortspec] Filter spec:
`{included: [..]} | {excluded: [..]} | {min?, max?}` with relative-date bounds; list columns
match if any item matches; the empty list matches `''`/`null`.

`WidgetOptions` carries the known keys typed (`widget`, `alignment`, `wrap`, `textColor`,
`fillColor`, `fontBold/Italic/Underline/Strikethrough`, `header*`, `dateFormat`, `timeFormat`,
`numMode`, `decimals`, `maxDecimals`, `currency`, `numSign`, `choices`, `choiceOptions`,
`rulesOptions`, `linkTarget`) plus `extra` for everything else. A field uses its own options
only if non-empty (`useColOptions`).

Card layout: `BoxSpec { leaf: Option<RowId>, size: Option<u8>, children: Vec<BoxSpec>, collapsed: Vec<BoxSpec> }`,
alternating HBox/VBox by depth, reconciled with the field list on load.[^grist-boxspec]

# View nodes

| Node | Depends on | Output |
|---|---|---|
| `view:section:{id}:linkfilter` | `controller:section:{src}:cursor`, `controller:section:{src}:selection`, `view:section:{src}:rows`, the link columns' `model:` nodes | `LinkFilter { filters: IndexMap<ColumnName, Vec<Value>>, operations: IndexMap<ColumnName, In \| Intersects \| Empty>, disable_editing: bool, default_values: ColumnValues }` |
| `view:section:{id}:rows` | `model:{T}.#rows`, sort columns, filter columns, `linkfilter`, `controller:section:{id}:filterdraft`, `model:acl`, `controller:user` | `Vec<RowId>` in the view store, token bumped |
| `view:section:{id}:cells` | `rows`, `model:acl`, `controller:user` | censor mask |
| `view:section:{id}:styles` | `rows`, each rule column `model:{T}.gristHelper_*Rule*`, section `rulesOptions` | per-row, per-field resolved `Style` index |
| `view:section:{id}:cursor_pos` | `rows`, `controller:section:{id}:cursor` | clamped `(row_index, field_index)` |
| `view:page:{id}:layout` | `_grist_Views.layoutSpec`, section list, `model:acl` | tree of section ids with sizes |
| `view:pages` | `_grist_Pages`, `model:acl` | page tree |

Link types, as Grist names them:[^grist-linking]

| Case | Condition | Filter |
|---|---|---|
| `Filter:Summary-Group` | src is summary, srcCol is `group` | tgt `id in group` |
| `Filter:Col->Col` | both columns | tgt `tgtCol == src row's srcCol` (`in` or `intersects` for lists) |
| `Filter:Row->Col` | tgtCol only | tgt `tgtCol == src row id` |
| `Show-Referenced-Records` | src RefList, no tgtCol | tgt `id in list` |
| `Cursor:Reference` | src Ref, no tgtCol | moves tgt cursor to the referenced row |
| `Summary` | no columns, src is a summary of tgt or a coarser summary | one filter per group-by column |
| `Cursor:Same-Table` | same table, no columns | cursor follows |

A cursor on the "new row" in the source yields an empty target with `disable_editing = true`;
`default_values` seeds a new target row to satisfy the link, as Grist's `getDefaultColValues`.
Cursor cycles between sections resolve by the most recent `edit` sequence in the cursor node,
exactly Grist's `[rowId, lastCursorEdit]` propagation.

# Row-list computation budget

`view:section:{id}:rows` recomputes only when a dependency changed; for a 100k-row table with
one sort column and one filter, a full rebuild is a sort of 100k keys (about 8 ms) and happens
on sort/filter changes; data edits rebuild incrementally by removing and reinserting the dirty
rows (binary search on the sort key). The grid never asks for more than the visible window from
this list.

# Conditional formatting

Rule columns are formula columns (`gristHelper_ConditionalRule` per field or column,
`gristHelper_RowConditionalRule` on the raw section for row rules) whose values are truthy per
row; `view:section:{id}:styles` combines them with the parallel `rulesOptions` styles (first
matching rule wins per property, Grist's order). Styles: `textColor`, `fillColor`, `fontBold`,
`fontItalic`, `fontUnderline`, `fontStrikethrough`.

[^grist-linking]: LinkingState.ts (link types, filter output, cursor propagation)
[^grist-sortspec]: SortSpec.ts and FilterState.ts (sortColRefs and filter JSON)
[^grist-boxspec]: BoxSpec.ts (layoutSpec)
