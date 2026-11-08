---
type: Requirement
title: "Requirements: actions, engine and graph"
description: "REQ-ACTION, REQ-ENGINE and REQ-GRAPH: user actions, inverses, atomic bundles, glitch-free recalculation through Causl, relations, lookups, summaries, cycles, trigger formulas, the facade."
tags: [requirements, actions, engine, causl]
status: draft
requirement_id: REQ-ACTION/REQ-ENGINE/REQ-GRAPH
priority: must
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

| Id | Requirement | Priority | Verification |
|---|---|---|---|
| REQ-ACTION-01 | All Grist user actions except the import transforms and `EvalCode` are implemented with Grist's expansion into doc actions, including the 18 metadata hooks. | must | `test_useractions.py`, `test_column_actions.py`, `test_table_actions.py` ports |
| REQ-ACTION-02 | Every applied doc action records its Grist-defined inverse; `ApplyUndoActions` restores data tables exactly; redo re-applies. | must | proptest 2; `test_undo*.py` ports |
| REQ-ACTION-03 | A bundle is atomic: on any error nothing in the document, store or graph changes. | must | proptest 1 |
| REQ-ACTION-04 | Bundles serialise to JSON equal in shape to Grist's `LocalActionBundle` (`actionNum`, `stored`, `undo`, `direct`, `retValues`, `info`). | must | schema test against Grist's TypeScript types rendered as JSON Schema |
| REQ-ENGINE-01 | After any bundle, every formula cell equals a fresh evaluation of its formula (glitch-free, complete). | must | proptest 3; `sb check` on fixtures |
| REQ-ENGINE-02 | Recalculation is incremental: a change to k cells of a data column recomputes only the dependent rows mapped through relations, never whole columns, unless a formula or schema changed. | must | proptest 4; `commit_single_cell_100k` bench under 150 us |
| REQ-ENGINE-03 | Dependencies are discovered by tracked reads and stale edges are dropped when a formula stops reading a column. | must | proptest 5; `test_lookup_relations.py` |
| REQ-ENGINE-04 | `lookupRecords`, `lookupOne`, `CONTAINS`, `order_by`, `find.*`, summary tables (auto rows, auto-remove, detach), display columns, rule columns, two-way references and trigger formulas behave as in Grist. | must | the ported sandbox suites listed in [testing](../quality/testing.md) |
| REQ-ENGINE-05 | Column-level cycles with row-level acyclic formulas (running totals, `PREVIOUS`) evaluate correctly; true cycles yield `#CIRCULAR` per cell, never a failed bundle. | must | `test_prevnext.py`, `test_formula_error.py` cycle cases |
| REQ-ENGINE-06 | The engine is deterministic: same document plus same actions plus pinned `--now` gives identical stored actions and values. | must | run the golden suite twice and diff |
| REQ-GRAPH-01 | All dependency tracking, ordering and notification go through `sheetbase-graph::Graph`; no other crate depends on `causl-engine-core`. | must | `cargo tree` check in `xtask layers` |
| REQ-GRAPH-02 | `CauslGraph` and `ReferenceGraph` are observationally equivalent on random schemas and action sequences. | must | differential proptest, 1000 cases |
| REQ-GRAPH-03 | Node values are version tokens; no row data enters the graph. | must | debug assertion on `Token` size; code review |
| REQ-GRAPH-04 | Namespaces `model:`/`controller:`/`view:` are enforced: a `model:` node never depends on the other two. | must | unit test expecting `NamespaceViolation` |
| REQ-GRAPH-05 | Facade overhead stays under 5 percent of Causl's own transition time on `recalc_chain_1024`. | should | bench gate |
| REQ-ENGINE-07 | Long bundles report progress every 50 ms and can be cancelled with a full rollback. | should | kittest with a 1M-cell paste |
