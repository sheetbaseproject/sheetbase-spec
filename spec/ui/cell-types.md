---
type: Reference
title: Cell types, renderers and editors
description: Grist's column type x widget matrix as the cell-type registry, each with its renderer, editor, capabilities (type-to-edit, Space behaviour, commit advance) and the xldatagrid cell types that fold into it.
tags: [ui, cells, editors]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-usertype
    resource: https://github.com/gristlabs/grist-core/blob/main/app/client/widgets/UserType.ts
    title: UserType.ts (type to widget registry)
  - id: xdg-celltypes
    resource: /Users/rom/workspace/xldatagrid/xldatagrid/packages/core/src/types/cell-types.ts
    title: xldatagrid cell-types.ts (27 CellType members and descriptor capabilities)
---

# Registry

```rust
pub struct CellTypeDesc {
    pub id: &'static str,                      // "Text/TextBox", "Numeric/Spinner", ...
    pub column_types: &'static [ColumnTypeKind],
    pub widget: &'static str,                  // widgetOptions.widget value
    pub render: fn(&RenderCtx, &Value, &WidgetOptions, &mut egui::Painter, Rect),
    pub editor: Option<fn() -> Box<dyn CellEditor>>,
    pub caps: CellCaps,                        // from xldatagrid descriptors
    pub codec: CellCodec,                      // clipboard text, csv, paste coercion
}
pub struct CellCaps { pub type_to_edit: bool, pub space: SpaceAction /* Select | Toggle | Open */, pub commit_advance: Advance /* Move | Stay */, pub focus: Focus /* Grid | Widget */, pub pasteable: bool }
pub trait CellEditor {
    fn open(&mut self, cell: CellAddr, initial: EditorSeed /* Current | Replace(SmolStr) | Formula */);
    fn ui(&mut self, ui: &mut egui::Ui, rect: Rect, ctx: &EditorCtx) -> EditorEvent;   // None | Commit(Value, Advance) | Cancel | GrowTo(Rect)
    fn value(&self) -> Result<Value, EditParseError>;
}
```

# Grist matrix[^grist-usertype]

| Column type | Widgets (default first) | Editor | Caps | xldatagrid types folded in[^xdg-celltypes] |
|---|---|---|---|---|
| Text | TextBox, Markdown, HyperLink | TextEditor (single line, grows; Shift+Enter newline when `wrap`) | type-to-edit, Move | text, password (via a `password` widgetOption, masked render), richText (Markdown widget renders GFM read-only; edit as text; TipTap composer dropped) |
| Numeric | TextBox, Spinner | NumericEditor (`inputMode` decimal, Up/Down step by `decimals`) | type-to-edit, Stay (xdg) | numeric, currency (numMode `currency` + `currency` option), slider (Spinner widget renders a slider when `widgetOptions.slider` is set; sheetbase extension), range/numericRange (dropped, see traceability) |
| Int | TextBox, Spinner | NumericEditor (integers) | type-to-edit, Stay | numeric |
| Bool | TextBox, CheckBox, Switch | none (Space/click toggles) | Toggle | boolean, booleanSelected |
| Date | DateTextBox | DateEditor (text + popup calendar) | type-to-edit, Move | calendar |
| DateTime | DateTimeTextBox | DateTimeEditor (date + time fields) | type-to-edit, Move | calendar |
| Choice | ChoiceTextBox | ChoiceEditor (dropdown with filter, create-new when allowed, colours from `choiceOptions`) | Open, Move | status, list, dropdown (single) |
| ChoiceList | ChoiceListCell | ChoiceListEditor (token field) | Open, Move | chipSelect, tags, compoundChipList (colours from `choiceOptions`), dropdown (multi), ordinalChips (dropped) |
| Ref | Reference | ReferenceEditor (dropdown over `visibleCol` values, shows id fallback) | Open, Move | dropdown (when options come from a table) |
| RefList | ReferenceList | ReferenceListEditor (token field) | Open, Move | measurement (dropped) |
| Attachments | AttachmentsWidget | AttachmentsEditor (viewer; no upload in v1) | Widget focus | upload, fileAttachment (viewer only) |
| Any | TextBox | TextEditor (formula columns are `Any` until typed) | type-to-edit, Move | |
| Id, ManualSortPos, PositionNumber | TextBox read-only | none | | |

Widget-level options honoured in rendering: `alignment`, `wrap`, `textColor`, `fillColor`,
`fontBold/Italic/Underline/Strikethrough`, number formats (`numMode` decimal/currency/percent/
scientific, `decimals`, `maxDecimals`, `numSign` parens), `dateFormat`/`timeFormat` (moment
tokens), `choiceOptions` colours, `linkTarget` for HyperLink. Formatting is through the harvested
`numfmt` crate for numbers (Grist's `NumberFormat` options are translated to a format code) and
`jiff` for dates.

# Formula editor

Any cell of a formula column (or `=` in a data cell) opens the FormulaEditor: monospace,
multi-line (grows to 10 lines, then scrolls), `$` autocomplete of columns, table and function
names, error underline from `CompileError.span`, Tab accepts completion, Enter commits,
Shift+Enter newline, Esc cancels. gridcraft's `code_editor.rs` is the base.

# Display of special values

| Value | Render |
|---|---|
| `Error` | `#NAME`-style short code (`#TYPE`, `#VALUE`, `#CIRCULAR`, `#PYTHON`, `#FUEL`, `#DIV/0`) in `error` colour, left aligned; tooltip shows the message; details on demand |
| AltText (wrong type) | the raw text in `error` colour with a dotted underline |
| `Censored` | hatched cell, no text, tooltip "hidden by access rules" |
| dangling `Ref` | `#Ref` plus the id, `warning` colour |
| `Null` in Bool CheckBox | indeterminate box |

# Tests

Each cell type has a `kittest` test for render at 1x and 2x, an editor open/commit/cancel
test, a paste coercion table test, and a snapshot in both themes.

[^grist-usertype]: UserType.ts (type to widget registry)
[^xdg-celltypes]: xldatagrid cell-types.ts (27 CellType members and descriptor capabilities)
