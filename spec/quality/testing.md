---
type: Component Design
title: Testing strategy
description: Unit tests per module, proptest over the engine and the graph facade with a differential oracle, golden tests against the 118 Grist fixture documents and the ported sandbox test suites, egui_kittest UI tests with snapshots, fuzzing, and what gates a PR.
tags: [quality, testing]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-fixtures
    resource: https://github.com/gristlabs/grist-core/tree/main/test/fixtures/docs
    title: grist-core test/fixtures/docs (118 .grist documents)
  - id: grist-sandbox-tests
    resource: https://github.com/gristlabs/grist-core/tree/main/sandbox/grist
    title: sandbox/grist/test_*.py (70 test modules)
---

# Layers

| Layer | Tool | What |
|---|---|---|
| Unit | `cargo test`, `insta` 1.49 for text snapshots | every module; error enums' `code()` stability; marshal codec; SQL DDL text |
| Property | `proptest` 1.12, 1000 cases minimum per property (Causl's own floor) | engine invariants below |
| Differential | proptest with both `Graph` backends | `CauslGraph` and `ReferenceGraph` produce identical store contents and identical `changed` sets for random action sequences on random schemas |
| Golden | fixture documents + ported Python tests | see below |
| UI | `egui_kittest` 0.37 with `wgpu` + `snapshot` | behaviour (events to commands), accessibility tree, pixel snapshots at ppp 1.0 and 2.0 in both themes, `kittest.toml` threshold 0.6, `max_failed_pixels = 0` |
| Fuzz | `cargo fuzz` (nightly job) | `sfl::parse`, `sfl::evaluate` with a mock `RecordSource`, `marshal::loads`, `store::decode`, `grist::decode_value`, `acl::Predicate::parse`, `import::csv` |
| Bench | `criterion` 0.8 + `cargo xtask bench --gate` | [performance budgets](performance-budgets.md) |

# Engine properties (proptest)

1. **Atomicity**: for any bundle that fails at any step, the `Document`, the `ColumnStore` and
   the graph registry are byte-identical to before (serialise and compare).
2. **Inverse round trip**: apply bundle `B`, apply its `undo`, the data tables equal the
   original; apply the original `stored` again (redo), equal the post-`B` state.
3. **Glitch-freedom**: after any commit, for every formula column and every live row, the
   stored value equals a fresh evaluation of the formula against the current store (`sb check`
   semantics as a property).
4. **Dirty-set soundness**: recomputing only `affected_rows` produces the same result as a
   full recompute (compare against `ReferenceGraph` run with `RowSet::All` forced).
5. **Relation reset**: after a formula changes its reads (random formula mutation), the
   dependency set equals the set of columns actually read in the last evaluation (no stale
   edges).
6. **Relabeling**: `PositionNumber` insertions keep strict ordering and emit the minimal
   adjustment set Grist's `relabeling.py` would (ported `test_relabeling.py` cases plus random).
7. **Schema consistency**: after any schema action sequence, `Schema::rebuild(meta) ==
   Document.tables` shape.
8. **Marshal**: `loads(dumps(v)) == v` for random `MarshalValue`; `dumps(loads(b)) == b` for
   every fixture blob.
9. **Selection FSM**: see [selection](../ui/selection.md).
10. **Value encoding**: `from_grist(to_grist(v, ty)) == v` for every `(Value, ColumnType)` pair
    where `ty.accepts(v)`.

# Golden tests

- **Fixture corpus**:[^grist-fixtures] every `.grist` in `fixtures/grist/` must (a) open, (b)
  migrate to v47 if older, (c) compile its formulas with the compile rate recorded, (d)
  recompute with `sb check` reporting zero differences for every formula whose dialect is
  `both`/`sfl` and `ok`, (e) round-trip save to `.sheetbase` and reopen with identical data
  tables, (f) for documents already at v47, "save as .grist" produces data tables whose SQL
  dump equals the input's (byte-identical rows for every user table).
- **Ported sandbox tests**:[^grist-sandbox-tests] `test_engine.py`, `test_lookups.py`,
  `test_lookups_refs.py`, `test_lookup_sort.py`, `test_lookup_find.py`, `test_summary.py`,
  `test_summary_choicelist.py`, `test_summary_groups.py`, `test_summary_undo.py`,
  `test_twoway_refs.py`, `test_reflist_rel.py`, `test_trigger_formulas.py`,
  `test_trigger_expression.py`, `test_default_formulas.py`, `test_derived.py`,
  `test_display_cols.py`, `test_rules.py`, `test_rules_grid.py`, `test_renames.py`,
  `test_rename_relations.py`, `test_undo.py`, `test_formula_undo.py`, `test_undo_rename.py`,
  `test_column_actions.py`, `test_table_actions.py`, `test_useractions.py`, `test_temp_rowids.py`,
  `test_relabeling.py`, `test_types.py`, `test_date_types.py`, `test_formula_error.py`,
  `test_codebuilder.py`, `test_gencode.py` (the parts about `$` rewriting), `test_prevnext.py`,
  `test_record_func.py`, `test_recordlist.py`, `test_acl_formula.py`, `test_acl_renames.py`,
  `test_predicate_formula.py`, `test_locked_tables.py`, `test_migrations.py`, `test_objtypes.py`,
  `test_sort_key.py`, `test_sort_spec.py`, `test_twowaymap.py`, `test_match_counter.py`,
  `test_replace_table_data.py`, `test_side_effects.py`, `test_dropdown_condition*.py`. These
  tests are written as `apply_user_actions` sequences with expected `stored`/`undo` actions and
  table data; `xtask fixtures port-test <name>` converts a Python test's action tables into a
  JSON case file (`tests/golden/<name>.json`) that the Rust harness runs. Tests depending on
  Python-only formulas are marked `skip: python` with the reason.
- **Formula doctests**: Grist's function docstrings' `>>>` examples, extracted to a table.
- **Clipboard HTML**: fixtures of Grist's HTML flavour for paste.

# UI tests

Every widget in [the catalogue](../ui/widgets.md) has a `kittest` module. The xldatagrid
Playwright catalogue is the behavioural checklist for the grid; each ported case names its
source spec in a comment. Snapshots live in `crates/sheetbase-ui/tests/snapshots/`; a changed
snapshot needs the PR to say why.

# Gates on a PR

`cargo xtask ci`: fmt, clippy `-D warnings`, `cargo deny` (licences, bans, advisories), unit +
property + golden (fast subset: 30 fixtures), kittest without snapshots, layers check, bench
gate on the engine suite (UI benches run nightly on the GPU runner). Nightly: full fixtures,
snapshots, fuzz 30 minutes per target, UI benches.
