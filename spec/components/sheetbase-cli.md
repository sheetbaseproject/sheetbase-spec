---
type: Component
title: sheetbase-cli
description: "L4 crate, the headless binary sb: info, check, recalc, export, import, apply, undo, redo, history, formula eval, migrate, explain, schema, bench, fixtures, serve (JSON-RPC over stdio)."
tags: [component, crate, cli, headless, agents]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Responsibilities

Subcommands and the JSON contract in [CLI surface](../cli/surface.md). `serve` is a
single-threaded loop reading newline-delimited JSON-RPC 2.0 from stdin and writing responses and
notifications to stdout; `--json` output everywhere is the serde form of the core types with
stable `code()`s for errors; exit codes as specified.

# Dependencies

`clap 4`, `serde_json`, `sheetbase-core`, `sheetbase-store`, `sheetbase-import`,
`sheetbase-formula`, `sheetbase-graph` (for `--graph reference` in `check` and `bench`),
`criterion` (bench harness behind a feature), `anyhow` (binary only). No renderer.

# Size

About 3.5k lines.

# Requirements carried

REQ-CLI-01 to 04, REQ-AGENT-01, REQ-AGENT-02.
