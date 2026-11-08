---
type: Component
title: sheetbase-graph
description: L0 crate exposing the Graph facade trait with the CauslGraph backend (feature causl, default) over the public mirror and the ReferenceGraph oracle backend; string ids, namespaces, tracked reads, commits, subscriptions.
tags: [component, crate, causl, graph]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Purpose

The one place that knows Causl. Everything else talks to `Graph`. Signatures in
[Causl mapping](../model/causl-mapping.md).

# Features

- `causl` (default): `causl-engine-core = { git = "https://github.com/sheetbaseproject/causl-engine-core", tag = "...", default-features = false, features = ["std"] }`.
- `graph-hash`: enables Causl's `enumerator` feature for `State::hash` in differential tests.
- `explain`: keeps `PhaseStep`s per commit for `sb explain`.

# Modules

`registry` (string id to `NodeRef`, namespaces, generations), `causl` (the backend),
`reference` (the oracle), `staging` (`CommitStaging`, `ColumnStoreView` traits that core
implements; the graph crate defines the traits so it can run computes without depending on core),
`error`.

The staging and store *traits* live here (`trait ComputeHost`, `trait RowSetLike`) so the crate
stays L0; `sheetbase-core` provides the implementations.

# Dependencies

`causl-engine-core` (optional), `smallvec`, `smol_str`, `indexmap`, `thiserror`. No std I/O.
`#![forbid(unsafe_code)]`.

# Size

About 2.5k lines: registry 400, causl backend 700, reference backend 600, traits and errors
300, tests 500 (plus the differential proptest in `tests/`).

# Requirements carried

REQ-GRAPH-01 to 05.
