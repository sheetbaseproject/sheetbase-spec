---
type: Overview
title: Repo and crate topology
description: Three repos under sheetbaseproject (spec, cargo workspace, Causl mirror) and eight crates in one workspace, each boundary justified.
tags: [overview, topology, crates]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Repos

| Repo | Contents | Licence | Why it is its own repo |
|---|---|---|---|
| `sheetbaseproject/sheetbase-spec` | this OKF bundle, the validator | Apache-2.0 | The spec has its own review cadence and its own readers; it must not be buried under cargo noise, and OKF wants a bundle to be a directory you can ship on its own. |
| `sheetbaseproject/sheetbase` | the cargo workspace with every crate below, fixtures, benches | Apache-2.0 | One workspace means one `Cargo.lock`, one CI matrix, atomic cross-crate refactors. The panel considered one repo per crate and rejected it: at specification stage nothing has a release cadence of its own, and the cost of coordinating eight repos is paid every day while the benefit (independent versioning) is paid never. See [ADR-002](../decisions/adr-002-repo-topology.md). |
| `sheetbaseproject/causl-engine-core` | public mirror of the `causl-engine-core` crate from the private Gitea upstream, synced by tag | MIT (upstream's) | Contributors without Gitea access must be able to build. MIT allows the mirror; the crate is `publish = false` and version `0.0.0` upstream so crates.io is not an option until upstream changes that. See [ADR-003](../decisions/adr-003-causl-dependency.md). |

Fixture documents (the 118 `.grist` files from grist-core's `test/fixtures/docs`, Apache-2.0)
live in `sheetbase/fixtures/grist/` with their licence notice; at 150 to 300 KB each they do not
justify a separate repo or LFS.

# Crates (all in `sheetbaseproject/sheetbase`)

```
sheetbase/
  Cargo.toml                 workspace, resolver = "3", rust-version = "1.89"
  crates/
    sheetbase-core/          document model, user and doc actions, engine, relations, view model
    sheetbase-formula/       lexer, parser, compiler, interpreter, function library, Value
    sheetbase-graph/         Graph trait + CauslGraph (feature "causl", default) + ReferenceGraph
    sheetbase-store/         SQLite (rusqlite bundled), schema v47 compat, action history, marshal codec
    sheetbase-import/        .grist open, csv/tsv, xlsx (calamine in, rust_xlsxwriter out)
    sheetbase-ui/            egui widgets: grid, cards, chart, editors, pages, theming
    sheetbase-app/           eframe desktop binary `sheetbase`
    sheetbase-cli/           headless binary `sb`
  fixtures/grist/            golden .grist documents (Apache-2.0, with NOTICE)
  third_party/               NOTICE entries for harvested gridcraft files
  xtask/                     cargo xtask: layers, bench gates, fixture refresh
```

Layering is enforced by `cargo xtask layers` (the idea is lifted from gridcraft's
`xtask/src/layers.rs`): a crate may only depend on crates in lower layers.

| Layer | Crates | May depend on |
|---|---|---|
| L0 | `sheetbase-formula`, `sheetbase-graph` | external crates only |
| L1 | `sheetbase-core` | L0 |
| L2 | `sheetbase-store`, `sheetbase-import` | L0, L1 |
| L3 | `sheetbase-ui` | L0 to L2 |
| L4 | `sheetbase-app`, `sheetbase-cli` | everything |

No crate below L3 depends on egui, eframe, winit, rfd or arboard. `sheetbase-formula` does not
depend on `sheetbase-core`: formulas evaluate against a `trait RecordSource` that core
implements, so the language can be tested and fuzzed alone.

# Each boundary, justified

- **formula / core.** The formula language is the most security-sensitive and most testable
  piece. Keeping it free of the document model lets it be fuzzed with no SQLite and no graph in
  the loop, and lets `sb formula eval` run with nothing else linked.
- **graph / core.** The facade exists so the Causl dependency is a feature, not a fate. The
  `ReferenceGraph` backend (a plain topological recompute) is the differential-test oracle and
  the fallback for a contributor who cannot or will not fetch the mirror.
- **store / core.** Core is in-memory and has no SQLite. That is what makes proptest over the
  engine fast and what keeps `.grist` compatibility (a storage concern: marshal blobs, affinity
  rules) from leaking into the engine.
- **import / store.** Import pulls in calamine, rust_xlsxwriter and csv parsing, none of which
  the engine needs. `.grist` opening lives in import rather than store because a Grist document
  is a *foreign* document until its formulas are classified (see
  [formula migration](../formula/migration.md)).
- **ui / app.** `sheetbase-ui` is a library of egui widgets testable with `egui_kittest`
  without a window. `sheetbase-app` is the eframe shell: window, menus, file dialogs, clipboard,
  settings.
- **cli.** Separate binary so headless use never links a renderer. It shares everything else.

# Rejected splits

- `sheetbase-server` as a crate: no headless multi-user server in v1 ([ADR-014](../decisions/adr-014-no-server-v1.md)). The CLI's `sb serve` subcommand (local JSON-RPC over stdio, for agents and tests) lives in `sheetbase-cli`.
- `sheetbase-grid` as its own crate separate from `sheetbase-ui`: the grid, the card view and the editors share the cell-type registry and the theme tokens; splitting them would force a fourth public API. Revisit if a second front end appears.
- `sheetbase-types` (shared value types): the `Value` enum belongs to `sheetbase-formula`, which is already L0. A fifth tiny crate would only add a hop.
