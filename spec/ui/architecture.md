---
type: Component Design
title: UI architecture
description: "How sheetbase-ui and sheetbase-app are put together: the eframe frame loop, the AppState, the command registry, the view store fed by Causl view nodes, and the rule that the UI only ever calls user actions."
tags: [ui, architecture, egui]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Layers

```
sheetbase-app (eframe)        window, menus, file dialogs (rfd), clipboard (arboard), settings, update loop
   |
sheetbase-ui                  pure egui: widgets that take &mut UiState and &DocView and emit Vec<Command>
   |         \
   |          commands: UserAction | UiAction (cursor, selection, open panel, ...)
   v
sheetbase-core::Engine        apply_user_actions(...) -> ActionBundle; controller: node writes for UiAction
   |
sheetbase-graph               one commit per frame at most (batched), view: nodes recomputed
```

Rule, taken from gridcraft's "thin UI" and xldatagrid's single commit chokepoint: a widget never
mutates the document. It returns commands. The app's frame loop collects them, batches the
`UiAction`s into one `controller:` commit and the `UserAction`s into one engine bundle (or one
per gesture when they must be separately undoable), applies them, and the next frame reads the
updated view nodes. This is also what makes `egui_kittest` tests deterministic: feed events, run
until settled, assert on commands and on the view.

# State

```rust
pub struct AppState {
    pub doc: Option<OpenDocument>,          // Engine + Document + path + dirty flag
    pub ui: UiState,                        // transient, not persisted (menus, drags, resize in progress, dialogs, focus)
    pub prefs: Prefs,                       // persisted via eframe storage: theme, font size, recent files, interface scale
    pub frame: FrameStats,                  // last frame ms, grid paint ms, fps, for the status bar and perf gate
    pub announcer: Announcer,               // a11y live region queue
    pub commands: Vec<Command>,             // collected this frame
}

pub struct DocView<'a> {                    // read-only handle the widgets get
    pub doc: &'a Document,
    pub view_store: &'a ViewStore,          // row lists, censor masks, resolved styles, cursor positions from view: nodes
    pub graph_time: u64,                    // memo key for everything cached per frame
}

pub enum Command { User(UserAction, UndoGroup), Ui(UiAction), App(AppAction) }
pub enum UiAction { SetCursor { section: RowId, row: RowId, field: RowId }, SetSelection { section, sel: SelectionState }, SetFilterDraft { .. }, OpenPage(RowId), OpenMenu(MenuId), CloseMenu, StartEdit { .. }, CancelEdit, .. }
pub enum AppAction { Open(PathBuf), Save, SaveAs(PathBuf), Export { .. }, Quit, ToggleTheme, SetScale(f32), CopyToClipboard(ClipboardPayload), RequestPaste, .. }
```

`UiState` mirrors xldatagrid's `GridInteractionState` reducer (menu, column drag, column group
drag, resize, row drag, filter menu, condition dialog, width and row-height overrides) as a
Rust enum-driven reducer with the same 29 actions, so its unit tests port directly.

# Command registry

gridcraft's `CommandSpec` pattern, adapted: every user-facing command (menu item, shortcut,
context menu entry) is a `CommandId` with `label`, `shortcut`, `enabled(&AppState) -> Result<(),
DisabledReason>`, `run(&mut AppState) -> Vec<Command>`. Menus and the shortcut table are built
from the registry, so a shortcut always matches its menu label and `F1` can render the full
shortcut list from the same data.

# Frame loop

1. Collect input events; the grid's keyboard module runs `decide()` on them.
2. Widgets paint from `DocView` and push `Command`s.
3. Apply: `UiAction`s to one `controller:` commit; `UserAction`s to the engine (each gesture is
   one bundle; a paste is one bundle with `linkId` chaining).
4. If anything changed, `ctx.request_repaint()`; otherwise egui idles (no busy loop; marching
   selection animation requests repaint at 60 Hz only while active).

# Windows and dialogs

One native window per document (gridcraft's `doc_windows.rs` via `eframe` viewports). Dialogs
are egui `Window`s with focus trapping (`Tab` cycles within, `Esc` closes), never native except
file open/save (rfd). The import wizard is a multi-step dialog driven by `sheetbase-import`'s
`ImportPlan`.
