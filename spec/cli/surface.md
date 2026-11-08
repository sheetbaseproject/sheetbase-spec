---
type: Component Design
title: CLI surface
description: The `sheetbase` desktop binary's flags and the `sb` headless tool's subcommands, JSON output contract, exit codes, and the sb serve JSON-RPC methods.
tags: [cli, headless, agents]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# `sheetbase` (desktop)

```
sheetbase [FILE...] [--new] [--page <name>] [--theme light|dark|system] [--scale <pct>] [--reduce-motion]
          [--as-user email=<e>,access=owners|editors|viewers] [--log <level>] [--version]
```

`FILE` may be `.grist` or `.sheetbase`. Multiple files open multiple windows. `--as-user` is
for testing access rules in the GUI. clap 4 with derive; `--help` is generated from the same
`CommandSpec` labels the menus use.

# `sb` (headless)

```
sb <command> [options] [--json] [--quiet] [--now <rfc3339>] [--as-user ...] [--timeout <secs>]
```

| Command | Purpose | Key options |
|---|---|---|
| `sb info <file>` | schema version, tables with row counts, columns with types and dialect flags, pages, rule count | `--tables`, `--columns <table>` |
| `sb check <file>` | opens, migrates in memory, compiles formulas, recomputes, compares stored values with recomputed ones, validates schema consistency and rule parse | `--formulas` (compile report), `--strict-grist`, `--formula-cost`, `--fix` (writes recomputed values back) |
| `sb recalc <file>` | full recompute and save | `--dry-run` |
| `sb export <file> --table <T> \| --section <id>` | csv/tsv/xlsx/json with sort and filter of the section applied | `--format csv\|tsv\|xlsx\|json`, `--header label\|id`, `--out <path>` |
| `sb import <file> <source>` | csv/tsv/xlsx into a new table or an existing one | `--table <T>`, `--map <json>`, `--delimiter`, `--encoding`, `--sheet <name>`, `--dry-run` (prints the ImportPlan) |
| `sb apply <file> <actions.json>` | applies a JSON array of user actions as one bundle | `--desc <text>`, `--dry-run` (returns the bundle without saving) |
| `sb undo <file> [--steps n]` / `sb redo <file>` | walks the stored history | |
| `sb history <file>` | lists bundles | `--limit`, `--since <actionNum>` |
| `sb formula eval <expr> [--file <doc> --table <T> --row <id>]` | evaluates an SFL expression, with or without a record context | `--trace` (prints the dependency reads) |
| `sb formula check <file>` | same as `check --formulas` | |
| `sb migrate <file> --to sheetbase\|grist` | converts between extensions and validates convertibility | `--out` |
| `sb explain <file> --last` | prints the recompute order and relation deltas of the last commit (from `PhaseStep`s) | |
| `sb schema <file>` | JSON schema dump (tables, columns, types, formulas, rules) | `--compact` (prompt-sized text) |
| `sb bench <suite>` | runs engine benches against fixtures | `--gate` (fails on regression) |
| `sb fixtures refresh` | re-downloads the grist-core fixture corpus at a pinned commit and verifies hashes | |
| `sb serve <file>` | JSON-RPC 2.0 over stdio, single client | `--read-only`, `--as-user` |
| `sb version` | versions of every crate and of the Causl mirror tag | |

# JSON contract

With `--json`, stdout is exactly one JSON document per command (or one per line for `history`
and `serve` notifications), stderr carries human diagnostics. Error output is
`{"error": {"code": "<stable code>", "message": "...", "retryable": bool, "details": {...}}}`
where `code` is `Failure::code()` ([errors](../quality/errors.md)).

Exit codes: 0 ok, 1 generic failure, 2 usage, 3 file not found or unreadable, 4 schema too new
or corrupt, 5 denied by access rules, 6 formula compile errors (`check`), 7 values differ
(`check`), 8 timeout, 9 cancelled.

# `sb serve` methods

| Method | Params | Result |
|---|---|---|
| `doc.open` | `{path, readOnly?}` | `{docId, schemaVersion, tables: [...]}` |
| `doc.close` | `{}` | `{}` |
| `doc.schema` | `{compact?}` | schema dump |
| `doc.fetch` | `{table, rows?: [id], cols?: [name], typed?: bool}` | `TableData` in Grist's column-oriented shape with ACL applied |
| `doc.apply` | `{actions: [UserAction], desc?, dryRun?}` | `ActionBundle` (JSON) |
| `doc.undo` / `doc.redo` | `{steps?}` | `ActionBundle` |
| `doc.subscribe` | `{tables?: [name], sections?: [id]}` | `{subscriptionId}`; then notifications `doc.changed` with `{time, intent, changedNodes: [...], bundleNum}` |
| `doc.export` | as `sb export` | `{path}` or inline for json |
| `doc.check` | as `sb check` | report |
| `formula.eval` | `{expr, table?, row?}` | `{value, reads: [...]}` |
| `formula.complete` | `{source, offset, table}` | completions |
| `server.capabilities` | `{}` | `{methods, schemaVersion, sflVersion, causlTag}` |

Requests are processed strictly in order; a long `doc.apply` blocks the queue (single-threaded
engine), which is the documented contract. Notifications are flushed after each commit.
