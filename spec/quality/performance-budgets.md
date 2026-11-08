---
type: Component Design
title: Performance budgets
description: Numbers the implementation must hit, how each is measured, and the CI gate for each; engine, storage, import and UI.
tags: [quality, performance, benchmarks]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

Reference machine: the CI runner is the baseline; local numbers are informational. Every bench
is a `criterion` benchmark or a `kittest` timing, recorded in `bench/baselines/*.json`, and
`cargo xtask bench --gate` fails a PR when the p95 regresses more than 10 percent (engine) or 15
percent (UI) against the baseline.

# Engine (`sheetbase-core/benches`)

| Bench | Scenario | Budget (p95) | Why this number |
|---|---|---|---|
| `commit_single_cell_100k` | update one Numeric cell in a 100k-row table with 5 dependent formula columns (`$A*2`, `$B+$A`, lookups to a 1k-row table, SUM over a RefList of 10) | 150 us end to end (incl. SQL write) | 5 recomputes x (0.3 us engine + 1 to 5 us interpreter) is about 20 us; SQLite update plus history insert dominates |
| `commit_bulk_update_100k` | `BulkUpdateRecord` of 100k cells in one column with the same dependents | 800 ms | 500k row evaluations at about 1 us plus store writes; shown with progress |
| `recalc_chain_1024` | 1024 formula columns in a chain, 1 row, one input change | 1.2 ms | Causl's own chain bench is 0.3 us/node; our compute wrapper and token write must stay under 1 us/node (facade overhead gate: under 5 percent) |
| `lookup_fanout` | 10k rows each doing `lookupRecords` on a 100k-row table by a Ref key, one target row changes | 60 us | relation maps the change to about 10 referring rows; no full recompute |
| `summary_1000_groups` | 100k source rows, summary by one Choice column with 1000 groups, one source row changes group | 120 us | helper delta + 2 group recomputes |
| `open_world` | load `World.grist` (fixture) into memory | 20 ms | small fixture, dominated by SQLite read and formula compile |
| `open_1m_cells` | load a 100k x 10 synthetic document | 400 ms | SQLite read at about 100 MB/s plus decode |
| `undo_redo_1k` | 1000 single-cell edits then 1000 undos | 300 ms total | each undo is a normal bundle |
| `sfl_eval_simple` | `$A * $B + 1` | 1.0 us | tree walker over resolved ops |
| `sfl_eval_lookup` | `len(Orders.lookupRecords(Customer=$id))` | 5.0 us | index probe + relation record |
| `sfl_eval_text` | `$Name.upper() + " " + str($Count)` | 2.0 us | SmolStr allocation bound |
| `marshal_roundtrip` | 10k mixed values | 20 ms | |
| `csv_import_100k` | 100k rows x 10 columns, type guessing | 1.5 s | parsing plus one bundle of `BulkAddRecord` |
| `xlsx_import_100k` | same via calamine | 4 s | calamine decode dominates |
| `export_csv_100k` | formatted values with a sort | 600 ms | `numfmt` at ~200 ns/cell |

Memory: a 100k x 10 Numeric/Text document resident under 60 MB (store ~11 MB, SQLite page cache
16 MB, graph under 1 MB, galley cache 4 MB, history tail 2 MB, egui and wgpu the rest). Measured
by `sb bench memory` using `peak RSS` after open.

# Graph facade

| Bench | Budget |
|---|---|
| `facade_overhead_chain_1024` | `CauslGraph::commit` total minus Causl's own `transition` time under 5 percent |
| `node_create_10k` | 10k `create_derived` under 20 ms (document open path) |
| `reference_vs_causl_1024` | informational: shows the reference backend is slower (it is O(graph)); not gated |

# UI

See [UI performance](../ui/performance.md) for the frame-level gates (`grid_paint_900` under 6 ms,
`grid_scroll_100k` under 9 ms, `grid_edit_latency` under 30 ms, `open_fixture_world` under 150 ms).

# Startup

`sheetbase` cold start to splash under 300 ms; to first paint of a fixture under 500 ms.
Measured by the `app_startup` bench (process spawn to first frame log line).
