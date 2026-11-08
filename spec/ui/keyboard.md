---
type: Reference
title: Keyboard model
description: Every key binding of v1, merged from Grist's commandList and xldatagrid's keyboard controller, with the decide() contract that makes them testable without a window.
tags: [ui, keyboard]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-commands
    resource: https://github.com/gristlabs/grist-core/blob/main/app/client/components/commandList.ts
    title: commandList.ts (command names and default keys)
  - id: xdg-keyboard
    resource: /Users/rom/workspace/xldatagrid/xldatagrid/packages/viewmodel/src/keyboard-controller.ts
    title: xldatagrid keyboard-controller.ts (decide(), modality rules)
---

# Contract

```rust
pub fn decide(ev: &KeyEvent, snap: &GridSnapshot) -> Decision;
pub enum Decision { Pass, Handled, Intent(Intent), DeferToEditor }
pub struct KeyEvent { pub key: egui::Key, pub mods: Modifiers /* Ctrl and Cmd are one "Mod" */, pub text: Option<SmolStr>, pub composing: bool }
pub struct GridSnapshot { pub mode: Mode /* Idle | Editing | WidgetFocus | ReadOnly */, pub cursor: Option<CellAddr>, pub selection: SelectionState, pub cell_caps: CellCaps, pub on_new_row: bool, pub has_menu: bool }
```

Modifier meaning lives in one place (xldatagrid's rule): Shift = extend, Mod = jump/additive,
Shift wins when both apply to movement. Letter chords match case-insensitively. IME composing
passes everything through.

# Navigation (idle)[^grist-commands]

| Key | Action | Source |
|---|---|---|
| Arrows | move cursor one cell, clamp (no wrap) | both |
| Mod+Arrow | jump to the edge of the data run (xldatagrid `getEndJumpCell`) | xdg |
| Shift+Arrow | extend selection from anchor | both |
| Mod+Shift+Arrow | extend to edge | Grist `ctrlShift±arrows` |
| Tab / Shift+Tab | next/prev field; at row end wraps to next row's first field; at grid end `Pass` (focus leaves) | both |
| Home / End | first/last field of the row | Grist `moveToFirstField`/`moveToLastField` |
| Mod+Home / Mod+End | first/last cell | both |
| Mod+Up / Mod+Down | first/last record | Grist `moveToFirstRecord`/`moveToLastRecord` |
| PageUp / PageDown | move one visible page of rows | Grist `pageUp`/`pageDown` (settles the xdg inconsistency) |
| Alt+Up / Alt+Down | previous/next page in the page tree | Grist `prevPage`/`nextPage` |
| Ctrl+O / Ctrl+Shift+O | next/prev section (region) | Grist `nextRegion`/`prevRegion` |
| Ctrl+I | focus section header / next jump target | Grist |
| Space | view record as card | Grist `viewAsCard` |
| Escape | clear selection (one level per press: range to cell; cell stays) | xdg |

# Selection

| Key | Action |
|---|---|
| Mod+A | select all cells of the section (one step, no progression) |
| Shift+Space | select row (xdg gutter press semantics on keyboard) |
| Ctrl+Space | select column |
| Mod+Shift+A | copy link to the current cell (Grist `copyLink`) |

# Editing

| Key | Idle | Editing |
|---|---|---|
| Enter / F2 | begin edit with current value selected (Enter on `editable: false` moves down) | Enter: commit and stay (Grist `fieldEditSave`), then `Enter` advance per prefs: stay (Grist default) or down (xdg default); F2: no-op |
| Typing (printable, no Mod) | begin edit replacing content with the typed char (type-to-edit types only) | inserts |
| `=` | begin edit in formula mode (Grist `makeFormula`): converts an empty column to a formula column on commit | inserts |
| Shift+Enter | commit and move up (Grist `transformUpdate` in transform mode) | textarea newline in wrap mode |
| Alt+Enter | n/a | newline in text editor |
| Tab / Shift+Tab | n/a | commit and move right/left (Shift+Tab always moves, settles xdg) |
| Escape | n/a | cancel edit (Grist `fieldEditCancel`) |
| Delete / Backspace | clear selected cells (Grist `clearValues`); Backspace also clears (Grist) | editor default |
| Mod+D | fill selection down (Grist `fillSelectionDown`: copy top row into data columns) | n/a |
| Mod+; / Mod+Shift+; | insert current date / date-time | same |
| Alt+Down | open dropdown for Choice/Ref editors | same |

# Rows and columns

| Key | Action |
|---|---|
| Mod+Enter / Mod+Shift+Enter | insert record after / before |
| Mod+Shift+D | duplicate rows |
| Mod+Backspace / Mod+Delete | delete records |
| Alt+= / Alt+Shift+= | insert field after / before |
| Ctrl+M | rename field |
| Alt+Shift+- | hide fields |
| Alt+- | delete fields |

# Clipboard and history

| Key | Action |
|---|---|
| Mod+C / Mod+X / Mod+V | copy / cut / paste (through the OS clipboard, HTML + TSV) |
| Mod+Z / Mod+Shift+Z / Ctrl+Y | undo / redo / redo |

# Global

| Key | Action |
|---|---|
| Mod+F / Mod+G / Mod+Shift+G | find / find next / find previous |
| Mod+S | save |
| Mod+O | open |
| Mod+N | new document |
| Mod+W | close window |
| Mod+, | preferences |
| Mod+= / Mod+- / Mod+0 | interface scale up / down / reset (75..200 percent) |
| Ctrl+Alt+O | toggle creator panel (Grist `creatorPanel`) |
| F1 / Mod+/ | shortcuts list |
| F4 | accessibility settings (Grist `accessibility`) |
| F8 / Shift+F8 | next / previous error cell (xdg) |
| Menu / Shift+F10 (mac Ctrl+Enter) | cell context menu; Ctrl+ variant column menu; Alt+ variant row menu |

# Per-editor keys

Choice/Ref dropdown: Up/Down wrap, Home/End, PgUp/PgDn by 5, Enter picks, typing filters,
Escape closes without commit. ChoiceList/RefList: Enter adds and stays, Tab adds and commits
right, Backspace on empty removes last token, `,` `;` tokenise. Date picker: Left/Right one day,
Up/Down one week, Shift+Up/Down one month, PgUp/PgDn one month (Shift: year), Home/End week
ends, Enter commits, `T` today. Bool: Space toggles (no edit mode). Attachments: Enter opens
the viewer. Formula editor: Tab accepts the autocomplete, Shift+Enter inserts newline, Enter
commits.

# Not bound on purpose

Backspace in idle on a bool cell does nothing special; Ctrl+click on a cell is plain select
(additive only in drag and in the gutter); PgUp/PgDn inside an editor pass to it.

[^grist-commands]: commandList.ts (command names and default keys)
[^xdg-keyboard]: xldatagrid keyboard-controller.ts (decide(), modality rules)
