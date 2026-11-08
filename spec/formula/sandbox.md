---
type: Component Design
title: Formula sandbox
description: Formula code is untrusted; the interpreter has no host access by construction, and every resource it can consume is bounded with a named error on overflow.
tags: [formula, security, sandbox]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Threat model

A document is a file from anywhere. Its formulas run on open (if hashes changed) and on every
edit. The attacker controls formula text, column names, table names, cell values and metadata
JSON. Goals we defend: no code execution outside the interpreter, no file or network access, no
unbounded CPU or memory, no panic that takes the app down, no information leak across documents
(only one is open per process anyway), and no way for a formula to observe or mutate `controller:`
or `view:` state.

# By construction

- SFL has no `import` that does anything, no `open`, `exec`, `eval`, `__import__`, `getattr`
  on arbitrary objects, no attribute access on anything but `Value`-backed objects whose method
  tables are static Rust `match` arms. There is no object model to escape from.
- The interpreter touches the outside world only through `trait RecordSource`, whose
  implementation reads the column store and the lookup indexes. No `std::fs`, no `std::net`, no
  `std::process` in `sheetbase-formula` (`cargo deny` bans them, and `#![forbid(unsafe_code)]`
  on the crate).
- Computes run on the engine thread, synchronously, inside a Causl commit; they cannot spawn
  work.

# Bounded resources

| Resource | Limit (default) | On overflow | Setting |
|---|---|---|---|
| Operations per cell evaluation | 1,000,000 `Op`s | `#FUEL` cell error, evaluation stops | `formula.fuel` in `_sheetbase_Settings`, max 100M |
| Call depth (lambdas, comprehension nesting) | 64 | `#RECURSION` | fixed |
| String length | 1 MiB | `#SIZE` | fixed |
| Collection size (list, dict, set, RecordSet materialised) | 1,000,000 items | `#SIZE` | fixed |
| `range()` length | 10,000,000 | `#SIZE` | fixed |
| Regex | `regex` crate: linear time, size limit 1 MiB compiled, DFA size limit 10 MiB | `#VALUE` on compile failure | fixed |
| Numeric `**` | result non-finite | `#NUM` | fixed |
| Cells recomputed per commit | none, but a progress callback every 50 ms lets the UI show a bar and `Esc` cancels the bundle (rolls back) | `ActionError::Cancelled` | UI |
| Total engine time per commit (CLI) | `--timeout` (default none) | `ActionError::Timeout`, rolled back | CLI flag |

Memory: `Value` sizes are bounded by the string and collection caps; a cell cannot hold more
than ~24 MB (1M `Value`s). A pathological document with 1M cells each holding a 1 MiB string
is 1 TB and will fail allocation; the store's `set` returns `StoreError::OutOfMemory` through
`try_reserve`, caught at the bundle boundary, bundle rolled back.

# Panics

A panic inside a compute is a bug in sheetbase, not an attack vector, but the app still must
not die: computes run under `std::panic::catch_unwind` in the facade (Causl requires computes
not to panic; a caught panic becomes `ComputeFailure::Panicked { message }`, which maps to
`RaceClass::ComputeThrew`, which rejects the commit byte-identically). The cell shows
`#INTERNAL` with a "report this" affordance. Fuzzing (`cargo fuzz` targets `parse`, `evaluate`,
`marshal::loads`, `storage::decode`) runs nightly to make this path rare.

# Outside the sandbox

The *document* can still be large, slow or ugly. Nothing stops a formula from being `SUM(Table.all.Amount)`
in every row of a 100k table (10^10 operations). The fuel cap turns that into 100k `#FUEL`
errors in under a second instead of a hung app, and `sb check --formula-cost` reports the top
formulas by cost so the user can fix them.
