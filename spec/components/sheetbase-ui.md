---
type: Component
title: sheetbase-ui
description: "L3 crate of egui widgets: the grid, cards, chart, pages, creator panel, menus, dialogs, cell renderers and editors, theme, announcer, command registry; testable with egui_kittest without a window."
tags: [component, crate, ui, egui]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Public surface

```rust
pub struct UiState;  pub struct Prefs;  pub struct Theme;  pub enum Command;  pub struct DocView<'a>;
pub fn page_ui(ui: &mut egui::Ui, view: &DocView, state: &mut UiState, theme: &Theme, page: RowId) -> Vec<Command>;
pub fn shell_ui(ctx: &egui::Context, app: &mut AppStateView) -> Vec<Command>;    // panels, menus, dialogs
pub mod grid { pub struct GridWidget; pub mod selection; pub mod keyboard; pub mod pointer; pub mod clipboard; pub mod geo; }
pub mod cells { pub struct CellTypeDesc; pub trait CellEditor; pub fn registry() -> &'static [CellTypeDesc]; }
pub mod theme { pub struct Tokens; pub fn contrast(a: Color32, b: Color32) -> f32; }
pub mod a11y { pub struct Announcer; }
pub mod commands { pub struct CommandSpec; pub fn registry() -> &'static [CommandSpec]; }
```

# Modules

`shell`, `pages::{tree,raw,layout,new}`, `sections::{frame,sortfilter,link,custom}`, `grid::{widget,geo,paint,
interact,drag,drag_select,selection,keyboard,pointer,editor,clipboard,gutter,header,menus,new_row,located,glide,fill}`,
`cards::{single,list,layout}`, `chart`, `creator::{column,widget,page,convert,rules}`, `filters::{menu,condition}`,
`fields::chooser`, `find`, `menus::context`, `tooltip`, `status`, `history`, `acl::page`, `import::wizard`,
`export`, `settings::{doc,prefs}`, `help::{shortcuts,about}`, `errors::bar`, `progress`, `attachments::viewer`,
`pickers::{color,date}`, `cells::{registry,render,editor,autocomplete,format_cache,formula_editor,popup,parse_input}`,
`theme::{mod,fonts}`, `a11y::announcer`, `commands::registry`, `state::interaction`, `icons`, `strings`.

# Dependencies

`egui 0.37`, `egui_extras 0.37`, `egui_plot 0.37`, `accesskit` (through egui), `sheetbase-core`,
`sheetbase-formula`, `sheetbase-import` (for the wizard's `ImportPlan`), `pulldown-cmark`, `image`,
`skrifa` (fonts), `smol_str`, `lru`. Dev: `egui_kittest 0.37` with `wgpu`, `snapshot`.

# Size

About 30k lines (gridcraft's comparable grid+editor+theme code is about 12k; add cards, pages,
creator panel, filters, dialogs, 40 widgets with tests).

# Requirements carried

REQ-UI-01 to 10, REQ-A11Y-01 to 03, REQ-PERF-04 to 06.
