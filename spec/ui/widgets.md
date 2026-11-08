---
type: Reference
title: Widget catalogue
description: "Every egui widget sheetbase-ui provides outside the grid: pages, sections, card views, chart, creator panel, filter and sort UI, find, import wizard, access rules page, history, status bar, dialogs; each with its data source, commands emitted and test."
tags: [ui, widgets, catalogue]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

| # | Widget | Module | Data in | Commands out | Notes / origin |
|---|---|---|---|---|---|
| 1 | `AppShell` | `shell` | `AppState` | `AppAction` | menu bar (File, Edit, View, Insert, Data, Help), left panel toggle, right (creator) panel toggle, document title with dirty marker |
| 2 | `PageTree` | `pages::tree` | `view:pages` | `OpenPage`, `UpdateRecord _grist_Pages` (rename, reorder, indent via drag) | Grist's left panel; keyboard: Up/Down, Right/Left expand, Enter open, F2 rename |
| 3 | `RawDataList` | `pages::raw` | `_grist_Tables` | open raw section, `RemoveTable`, `RenameTable`, `DuplicateTable` | "Raw data" page with row counts |
| 4 | `PageLayout` | `pages::layout` | `view:page:{id}:layout` | `UpdateRecord _grist_Views.layoutSpec` (drag to resize/reorder sections) | Grist `Layout`; BoxSpec splitters with 6 pt handles |
| 5 | `SectionFrame` | `sections::frame` | `SectionRec` | section menu commands, `RemoveViewSection`, link setup | title bar with widget type icon, link badge, sort/filter bar, expand to full page |
| 6 | `GridWidget` | `grid` | see [grid](grid.md) | | |
| 7 | `CardView` (`single`) | `cards::single` | section, `BoxSpec`, one record | `UpdateRecord`, navigation | labels + cells per layout, field editors reuse the cell editors, Tab order = layout order |
| 8 | `CardListView` (`detail`) | `cards::list` | section rows | same | virtualised cards, same layout per card |
| 9 | `ChartView` | `chart` | section rows, `chartType`, `ChartOptions` | none (read-only) | bar, line, area, scatter, pie, donut via `egui_plot` 0.37 (MIT OR Apache-2.0); kaplan_meier dropped with a placeholder; axis formatting through `numfmt` |
| 10 | `CustomPlaceholder` | `sections::custom` | section options | none | shows widget URL and "custom widgets are not supported in this version" |
| 11 | `CreatorPanel` | `creator` | current section, field, column | `ModifyColumn`, `UpdateRecord` on field/section/view rows | tabs: Column (label, id, type, formula/data toggle, widget, format, choices, Ref target and show-column, conditional rules, description), Widget (title, type, row height, gridlines, frozen, sort, filter, link), Page |
| 12 | `TypeConverter` | `creator::convert` | column | `ConvertFromColumn`, `CopyFromColumn`, revert | the transform preview Grist shows when changing a type |
| 13 | `SortFilterBar` | `sections::sortfilter` | section sort spec, filters, drafts | `UpdateRecord sortColRefs`, `_grist_Filters` add/update/remove, `SetFilterDraft` | save/revert of unsaved state |
| 14 | `ColumnFilterMenu` | `filters::menu` | column values, counts | filter draft, sort | xldatagrid's Excel-365 filter menu: search, (Select All), (Blanks), live preview with savepoint, min/max for numeric and date, relative dates |
| 15 | `FilterConditionDialog` | `filters::condition` | | filter draft | custom AutoFilter with And/Or rows |
| 16 | `ColumnChooser` | `fields::chooser` | section fields, hidden columns | `AddRecord _grist_Views_section_field`, remove | searchable checklist |
| 17 | `FindBar` | `find` | current section rows and fields | cursor moves | Mod+F; searches formatted text; wraps; count badge; `Enter`/`Shift+Enter` |
| 18 | `ContextMenu` | `menus::context` | command registry | any | one implementation for cell/header/gutter/page/section menus; keyboard per [keyboard](keyboard.md) |
| 19 | `Tooltip` | `tooltip` | hovered cell | none | 400 ms delay singleton, cell text or error message or column description |
| 20 | `Announcer` | `a11y::announcer` | queue | none | AccessKit live node, see [a11y](a11y.md) |
| 21 | `StatusBar` | `status` | selection stats, row count, fps (debug), save state | none | Grist's `SelectionSummary` (sum/count of selected numeric cells) |
| 22 | `HistoryPanel` | `history` | `_sheetbase_ActionHistory` tail | undo to here | list of bundles with `desc`, time, user; Grist's Document History tab |
| 23 | `AccessRulesPage` | `acl::page` | rules, resources | `UpdateRecord` on rules (M7), read-only in M6 | table per resource, memo column, validation errors from `Predicate::parse` |
| 24 | `ImportWizard` | `import::wizard` | `ImportPlan` from `sheetbase-import` | `AddTable`, `BulkAddRecord`, column mapping | steps: source, mapping (new table or into existing, column match by name), preview with type guesses, conflicts (unique key strategy), done; xldatagrid's wizard structure |
| 25 | `ExportDialog` | `export` | section/doc | `AppAction::Export` | csv/tsv/xlsx, header as label or id, apply sort and filter |
| 26 | `DocumentSettings` | `settings::doc` | `_grist_DocInfo.documentSettings`, timezone, locale, currency | `UpdateRecord` | |
| 27 | `Preferences` | `settings::prefs` | `Prefs` | `AppAction` | theme (system/light/dark), high-contrast gridlines, interface scale, font size, Enter behaviour, recent files |
| 28 | `ShortcutsDialog` | `help::shortcuts` | command registry | none | F1 |
| 29 | `AboutDialog` | `help::about` | versions, NOTICE text | none | shows third-party notices (licence compliance surface) |
| 30 | `ErrorBar` | `errors::bar` | last `Failure` | retry when `retryable()` | non-modal, per [errors](../quality/errors.md) |
| 31 | `ProgressBar` | `progress` | long commit progress | cancel | shown after 300 ms of engine work |
| 32 | `AttachmentViewer` | `attachments::viewer` | `_gristsys_Files` blob | none | images inline (`image` crate), other types "open externally" |
| 33 | `ColumnHeaderMenu` | `grid::menus` | field | sort, freeze, hide, options | part of the grid |
| 34 | `RowMenu` | `grid::menus` | row | insert, duplicate, delete, view as card | part of the grid |
| 35 | `NewTableDialog` / `NewPageDialog` | `pages::new` | tables | `AddEmptyTable`, `AddView`, `CreateViewSection` (incl. summary group-by picker) | Grist's "Add New" menu |
| 36 | `LinkPicker` | `sections::link` | sections of the page | `UpdateRecord link*Ref` | lists valid link sources per Grist's `LinkingState` rules |
| 37 | `ConditionalRuleEditor` | `creator::rules` | column rules | `AddEmptyRule`, `ModifyColumn` on rule columns, `rulesOptions` | formula per rule plus style pickers |
| 38 | `ColorPicker` | `pickers::color` | | | palette + hex; from xldatagrid's palette picker, no gradient wheel |
| 39 | `DatePicker` | `pickers::date` | | | month grid, keyboard per [keyboard](keyboard.md) |
| 40 | `SplashScreen` | `shell::splash` | recent files | `Open`, `New`, import | first window when no document is open |

Not built: ribbon, backstage, sheet tabs (pages replace them), formula bar as a separate region
(the in-cell formula editor plus the creator panel's formula field cover it; a pinned formula bar
is an open question), name box, minimap, pagination, print.

Each widget has a `kittest` test module named after it and a snapshot per theme at 1x; the
catalogue table is the checklist for M5 to M7.
