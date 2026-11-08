---
type: Decision
title: "ADR-017: Named error enums per layer with a retryable flag and a defined UI behaviour per variant"
description: Every crate exposes one error enum; variants carry structured fields, implement a `retryable()` method, and the UI behaviour for each variant is specified in the errors concept; panics are bugs and the app process guards them like gridcraft's Session does.
tags: [decision, errors, api]
status: draft
decision_id: ADR-017
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Context

"Appropriate error handling" is not a specification. The API role asked for named enums; the
UI role asked for a behaviour per variant; the Rust role asked that cell errors (data) and
engine errors (control flow) never share a type.

# Decision

Two kinds, never mixed:

- **Cell errors are values**: `Value::Error(CellError)` ([ADR-015](adr-015-value-model.md)).
  They propagate through formulas like Grist's `RaisedException`, display as `#NAME`-style
  short codes in cells with the message in a tooltip, and never stop a commit.
- **Engine and I/O errors are `Result::Err`** with one enum per crate (`FormulaError`,
  `GraphError`, `StoreError`, `ImportError`, `ActionError`, `UiError`) and a shared
  `trait Failure { fn retryable(&self) -> bool; fn user_message(&self) -> String; fn code(&self) -> &'static str; }`.
  Each variant's `retryable`, user message and UI behaviour are tabulated in
  [errors](../quality/errors.md). Panics are bugs: the app wraps each frame's action dispatch in
  `catch_unwind` (gridcraft's `Session::execute` pattern), restores the last good document state
  from the staging overlay, logs with `tracing`, and shows a non-modal "something went wrong,
  your last action was rolled back" bar with a copy-diagnostics button.

Conventions: `thiserror` 2 for derives, no `anyhow` in library crates (allowed in the two
binaries), no `Box<dyn Error>` across crate boundaries, every variant that wraps an external
error names the operation (`StoreError::Sqlite { op: "open", source }`), never a bare `From`.

# Alternatives

**One global error enum.** Lost: it would make `sheetbase-formula` depend on SQLite error types.

**`anyhow` everywhere.** Lost: the UI cannot decide behaviour on an opaque chain.

# Consequences

- Error enums are part of the public API and are `#[non_exhaustive]` from 0.1.
- Each variant has a test asserting its `code()` is stable, because `sb --json` emits it.
