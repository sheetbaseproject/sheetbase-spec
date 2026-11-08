---
type: Component Design
title: UI performance
description: "The 60 fps budget for the grid and how it is met: visible-window painting, the galley cache keyed by node version, incremental row lists, memoisation rules, and the measured gates."
tags: [ui, performance]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Budget

16.6 ms per frame at 60 Hz. Allocation on the reference machine (Apple M-series laptop or a
2023 x86 laptop, 2x HiDPI, 1920x1200 pt window, a grid showing 45 rows x 20 columns = 900
cells, two sections on the page):

| Phase | Budget |
|---|---|
| egui input + layout of chrome (panels, menus) | 1.5 ms |
| view store reads (row window, styles, censor) | 0.3 ms |
| grid paint, both sections | 6.0 ms (about 3.3 us per visible cell) |
| selection, overlays, headers | 0.7 ms |
| egui tessellation + wgpu submit | 3.0 ms |
| headroom | 5.1 ms |

Engine work (a commit) is not in the frame budget: commits run before painting, and a commit
that exceeds 8 ms shows the progress bar after 300 ms and keeps the UI responsive by running the
compute loop in slices between frames (the Causl commit itself is atomic, so slicing happens at
the bundle level: a long paste is split into chunks of 5000 rows chained by `linkId`).

# Keeping the grid under 6 ms

- **Visible window only.** `Geo::visible_rows/cols` with 3/1 overscan. 900 cells painted, never
  the table.
- **Galley cache.** `GalleyCache: LruCache<(NodeVersion, RowId, FieldWidthPx, StyleHash, ZoomBits), Arc<Galley>>`
  sized 8192 entries (about 4 MB). The key includes the column node's version, so a cell's
  galley is reused across frames until its column changes. Hit rate while scrolling is above 90
  percent (only newly exposed rows lay out). gridcraft's quadrant painter lays out every cell
  every frame; that is the one thing we do differently from it.
- **Formatted text cache.** The view store caches the formatted string per `(column version,
  row)` alongside the galley; formatting numbers through `numfmt` is about 200 ns, dates about
  500 ns, so this cache mostly saves allocation.
- **Style resolution.** `view:section:{id}:styles` is a derived node; the grid reads a `u16`
  style index per visible cell and indexes a `Vec<ResolvedStyle>`; no per-cell `Style` clone
  (gridcraft's `look()` clones per cell; we do not).
- **Row list.** `view:section:{id}:rows` is incremental: data edits patch the sorted list by
  binary search; only sort or filter changes rebuild it.
- **No per-frame allocation in the hot loop**: the painter receives `&[Shape]` from a reused
  `Vec`; strings come from the cache; `SmolStr` for short texts.
- **Repaint on demand.** Idle frames are skipped by egui; we request repaints only on input,
  on commit, and at 60 Hz while an animation (selection glide, progress) is active.

# Memoisation rules (Causl guidance, applied)

Memoise on `graph_time` or a node's `version`, never on value identity. Every cache in
`sheetbase-ui` keys on `(node version, ...)`; `DocView.graph_time` invalidates frame-level
caches. A cached value is never compared by pointer.

# Gates (CI, `cargo xtask bench ui`)

Run with `egui_kittest` in wgpu headless mode on the reference CI runner (x86, software adapter
is too slow, so a GPU runner is required; results from the software adapter are informational):

| Bench | Scenario | Gate |
|---|---|---|
| `grid_paint_900` | 45x20 numeric and text cells, static | < 6.0 ms per frame p95 |
| `grid_scroll_100k` | 100k rows, wheel scroll 30 frames | < 9.0 ms per frame p95, galley cache hit > 85 percent |
| `grid_edit_latency` | type one char in a cell with 5 dependent formula columns over 100k rows | input to paint < 30 ms (commit ~10 us + 2 frames) |
| `grid_paste_10k` | paste 10k x 5 cells | < 1.5 s total, UI responsive (frame p95 < 33 ms during) |
| `page_two_sections` | grid + card list, 1920x1200 | < 12 ms per frame p95 |
| `open_fixture_world` | open `World.grist` to first paint | < 150 ms |

A regression over the gate by more than 10 percent fails the PR; numbers are recorded in
`bench/baselines/ui.json` and refreshed deliberately.

# HiDPI

All geometry in points, snapped to the pixel grid via `pixels_per_point` (gridlines at
`round(x * ppp) / ppp - 0.5 / ppp`). Galley keys include the zoom bits so 1x and 2x do not share
rasterisation. Snapshot tests run at ppp 1.0 and 2.0.
