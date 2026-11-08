---
type: Requirement
title: "Requirements: import/export, CLI, agents, security, app, engine performance"
description: REQ-IO, REQ-CLI, REQ-AGENT, REQ-SEC, REQ-APP and the engine side of REQ-PERF.
tags: [requirements, import, cli, security, performance]
status: draft
requirement_id: REQ-IO/REQ-CLI/REQ-AGENT/REQ-SEC/REQ-APP/REQ-PERF
priority: must
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

| Id | Requirement | Priority | Verification |
|---|---|---|---|
| REQ-IO-01 | csv/tsv import with encoding and delimiter sniffing, Grist's type guessing, into a new or existing table through an `ImportPlan` the user can edit. | must | `csv_import_100k` bench; `PasteParsing.grist`, `ImportReferences.grist` |
| REQ-IO-02 | xlsx import (one table per sheet) and export (whole document), csv/tsv export per section with sort and filter applied, header as label or id. | must | `Exports.grist` comparison against Grist's `ExportDSV` output |
| REQ-IO-03 | "Save as .grist" is offered only when convertible and explains what blocks it otherwise. | must | kittest; `sb migrate --to grist` on fixtures |
| REQ-IO-04 | Imports never truncate silently: over-cap inputs are refused with the cap named. | must | unit tests at the caps |
| REQ-CLI-01 | Every subcommand in [CLI surface](../cli/surface.md) exists, with `--json` emitting exactly one JSON document and stable error codes. | must | CLI integration tests |
| REQ-CLI-02 | Exit codes follow the table. | must | same |
| REQ-CLI-03 | `sb check` detects a stored value differing from a recomputed one and `--fix` repairs it. | must | doctored fixture |
| REQ-CLI-04 | `sb` links no renderer (binary size under 25 MB stripped). | should | size check in CI |
| REQ-AGENT-01 | `sb serve` exposes every user action and the fetch/schema/subscribe methods over JSON-RPC 2.0 on stdio, single client, in order. | must | integration test driving a document through stdin |
| REQ-AGENT-02 | `doc.schema --compact` fits a 50-table document in under 8k tokens of plain text. | should | measured on `Covid-19.grist` |
| REQ-SEC-01 | No crate below L4 opens a socket; `cargo deny` bans network crates in library crates. | must | `cargo deny` in CI |
| REQ-SEC-02 | Formula evaluation is pure and bounded ([sandbox](../formula/sandbox.md)); fuzz targets run nightly with zero crashes for 30 days before 1.0. | must | fuzz dashboard |
| REQ-SEC-03 | Every untrusted input (file, clipboard, import) has a size cap and a bounded parser; a malformed input yields an error, never a panic or hang. | must | fuzz targets per parser |
| REQ-SEC-04 | A panic during a command is caught, the last good state restored, and diagnostics offered; the app never exits on a document-triggered panic. | must | kittest injecting a panic |
| REQ-APP-01 | One window per document; open/save/save-as/recent files/dirty tracking; file associations for `.grist` and `.sheetbase`. | must | manual + kittest |
| REQ-APP-02 | Settings persist (theme, scale, Enter behaviour, high-contrast gridlines, reduce motion). | must | restart test |
| REQ-APP-03 | Cold start to splash under 300 ms, to first paint of `World.grist` under 500 ms. | should | `app_startup` bench |
| REQ-PERF-01 | `commit_single_cell_100k` under 150 us, `commit_bulk_update_100k` under 800 ms, `lookup_fanout` under 60 us, `summary_1000_groups` under 120 us. | must | bench gate |
| REQ-PERF-02 | `open_1m_cells` under 400 ms; resident memory for that document under 60 MB. | must | bench + `sb bench memory` |
| REQ-PERF-03 | Bench regressions over 10 percent (engine) or 15 percent (UI) fail the PR. | must | `cargo xtask bench --gate` |
