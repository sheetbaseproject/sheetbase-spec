---
type: Reference
title: Grist source map
description: Which grist-core file each sheetbase module reimplements (behaviour, not code), so a reader of the Grist source can find our counterpart and vice versa.
tags: [references, grist]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

No Grist source is copied; this map is for navigation and for golden-test provenance.

| grist-core path | sheetbase module | Notes |
|---|---|---|
| `sandbox/grist/schema.py`, `app/common/schema.ts` | `sheetbase-store::schema` (DDL), `sheetbase-core::meta` | schema version 47 |
| `sandbox/grist/migrations.py` | `sheetbase-store::migrations` | 1 to 47 |
| `sandbox/grist/usertypes.py`, `app/common/gristTypes.ts` | `sheetbase-core::types::ColumnType`, `sheetbase-formula::Value` | `accepts`, defaults |
| `sandbox/grist/objtypes.py`, `app/plugin/GristData.ts` | `sheetbase-core::wire` | `to_grist`/`from_grist` |
| `app/server/lib/DocStorage.ts` | `sheetbase-store::{codec,sql}` | affinities, `_encodeValue` |
| `app/server/lib/ActionHistoryImpl.ts` | `sheetbase-store::history` | we read marshal, write JSON |
| `sandbox/grist/actions.py`, `app/common/DocActions.ts` | `sheetbase-core::actions::doc` | |
| `sandbox/grist/docactions.py` | `sheetbase-core::actions::apply` | inverses |
| `sandbox/grist/useractions.py` | `sheetbase-core::actions::user` | 43 handlers, 18 `override_action` hooks |
| `sandbox/grist/action_obj.py`, `app/common/ActionBundle.ts` | `sheetbase-core::actions::bundle` | |
| `sandbox/grist/action_summary.py`, `app/common/ActionSummary.ts` | `sheetbase-core::actions::summary` | for the history panel |
| `sandbox/grist/relabeling.py` | `sheetbase-core::engine::relabel` | PositionNumber inserts |
| `sandbox/grist/depend.py` | `sheetbase-graph` (edges) + `sheetbase-core::engine::relation` (rows) | [ADR-005](../decisions/adr-005-relations-on-causl.md) |
| `sandbox/grist/relation.py` | `sheetbase-core::engine::relation` | |
| `sandbox/grist/engine.py` | `sheetbase-core::engine::{pipeline,compute,cycle_group}` | `_recompute_step` becomes the compute; `OrderError` lives in cycle groups |
| `sandbox/grist/lookup.py`, `lookupset.py`, `twowaymap.py`, `match_counter.py` | `sheetbase-core::engine::lookup` | |
| `sandbox/grist/summary.py`, `summary_helper.py` | `sheetbase-core::engine::summary` | |
| `sandbox/grist/column.py`, `table.py`, `records.py` | `sheetbase-core::store::ColumnStore`, `sheetbase-formula::sfl::record` | `Record`/`RecordSet` objects live in the formula crate |
| `sandbox/grist/codebuilder.py`, `gencode.py`, `textbuilder.py` | `sheetbase-formula::sfl::{lexer,parser,compile}` | `$` rewriting, implicit return, lazy args |
| `sandbox/grist/functions/*.py` | `sheetbase-formula::functions::grist` | wrappers over harvested gridcraft functions plus Grist-specific ones |
| `sandbox/grist/moment.py` | `sheetbase-formula::date` (over `jiff`) | format tokens |
| `sandbox/grist/acl.py`, `predicate_formula.py`, `app/common/ACLRuleCollection.ts`, `ACLPermissions.ts`, `GranularAccessClause.ts`, `PredicateFormula.ts` | `sheetbase-core::acl` | |
| `app/server/lib/GranularAccess.ts` | `sheetbase-core::acl::enforce` + `view_model` censoring | |
| `sandbox/grist/docmodel.py` | `sheetbase-core::meta::MetaIndex`, auto-removes | |
| `app/common/SortSpec.ts`, `FilterState.ts`, `ColumnFilterFunc.ts` | `sheetbase-core::view_model::{sort,filter}` | |
| `app/client/components/LinkingState.ts` | `sheetbase-core::view_model::linking` | as a `view:` node compute |
| `app/common/BoxSpec.ts`, `app/client/components/Layout.ts`, `RecordLayout.ts` | `sheetbase-ui::pages::layout`, `cards::layout` | |
| `app/common/WidgetOptions.ts`, `app/client/widgets/UserType.ts` | `sheetbase-core::types::WidgetOptions`, `sheetbase-ui::cells::registry` | |
| `app/client/components/commandList.ts` | `sheetbase-ui::commands::registry`, [keyboard](../ui/keyboard.md) | |
| `app/client/components/GridView.js`, `CopySelection.ts`, `Clipboard.ts`, `app/client/lib/tableUtil.ts` | `sheetbase-ui::grid::{paint,clipboard,drag}` | paste tiling, HTML flavour |
| `app/client/components/ChartView.ts` | `sheetbase-ui::chart` | |
| `app/server/lib/ExportDSV.ts`, `ExportXLSX.ts`, `Export.ts` | `sheetbase-import::export` | |
| `app/server/lib/ActiveDocImport.ts`, `sandbox/grist/imports/*` | `sheetbase-import::{csv,xlsx,plan}` | |
| `test/fixtures/docs/*.grist` | `sheetbase/fixtures/grist/` | golden corpus |
| `sandbox/grist/test_*.py` | `sheetbase/tests/golden/*.json` via `xtask fixtures port-test` | |
