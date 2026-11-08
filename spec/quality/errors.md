---
type: Reference
title: Error catalogue
description: Every error enum variant across the crates with its stable code, retryable flag, user message and the UI behaviour when it surfaces.
tags: [quality, errors, api]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

Conventions per [ADR-017](../decisions/adr-017-error-model.md). `retryable()` means "the same
call may succeed if repeated without the user changing anything" (a transient lock), not "the
user can fix it and try again".

# `ActionError` (sheetbase-core)

| Variant | Code | Retryable | User message | UI |
|---|---|---|---|---|
| `Denied { action, memo }` | `acl.denied` | no | "Access rules do not allow this." plus memo | toast, action dropped, cell reverts |
| `TableLocked { table }` | `acl.locked` | no | "Table T is locked." | toast |
| `FormulaColumnWrite { table, col }` | `action.formula_write` | no | "C is a formula column; edit the formula instead." | toast with "Edit formula" button opening the creator panel |
| `ProtectedSection { section }` | `action.protected_section` | no | "This section is required and cannot be removed." | toast |
| `UniqueReferenceViolation { table, col, row }` | `action.unique_ref` | no | "Row r would be referenced twice through C." | toast, edit reverts |
| `TooManyNewRows { count }` | `action.too_many_rows` | no | "Cannot add more than 1,000,000 rows at once." | dialog |
| `BadRule { rule_pos, reason }` | `acl.bad_rule` | no | "Rule n: reason" | inline in the rules page, bundle rolled back |
| `SchemaInconsistent { table, column, detail }` | `engine.schema_inconsistent` | no | "Internal consistency check failed; the change was rolled back." | error bar with diagnostics |
| `CycleUnresolved { columns }` | `engine.cycle` | no | "These formulas depend on each other: ..." | toast listing columns; cells show `#CIRCULAR` |
| `AutoRemoveLoop` | `engine.autoremove_loop` | no | "The change could not settle; rolled back." | error bar |
| `Cancelled` | `action.cancelled` | no | none | progress bar closes |
| `Timeout { secs }` | `action.timeout` | no | "Stopped after n s." (CLI only) | n/a |
| `Graph(GraphError)` | `graph.*` (inner code) | inner | inner | error bar |
| `Store(StoreError)` | `store.*` | inner | inner | inner |
| `Compile { table, col, error }` | `formula.compile` | no | compile message with span | underline in the editor; column keeps the previous formula until fixed |

# `GraphError` (sheetbase-graph)

| Variant | Code | Retryable | Behaviour |
|---|---|---|---|
| `Cycle { path }` | `graph.cycle` | no | core regroups once; if it recurs, `CycleUnresolved` |
| `ComputeFailed { node, reason }` | `graph.compute_failed` | no | error bar "Internal error in column C" with report button; bundle rolled back |
| `NamespaceViolation { from, to }` | `graph.namespace` | no | debug assertion in debug builds; error bar in release; programming error |
| `UnknownNode`, `Duplicate`, `Disposed` | `graph.node` | no | programming error, error bar |
| `Reentrant` | `graph.reentrant` | yes | the frame loop retries next frame |
| `Backend(msg)` | `graph.backend` | no | error bar, logged at error with the `RaceClass` |

# `StoreError` (sheetbase-store)

| Variant | Code | Retryable | Behaviour |
|---|---|---|---|
| `Sqlite { op, source }` | `store.sqlite` | `source.is_busy()` | busy: retry 5 times with backoff then error bar; else error bar "Could not op the document" |
| `Locked { path }` | `store.locked` | yes | dialog "Another process has this document open" with Retry / Open read-only |
| `SchemaTooNew { found, supported }` | `store.schema_too_new` | no | dialog, opens read-only |
| `SchemaTooOld { found }` | `store.schema_too_old` | no | "Cannot migrate from version n" (below 1) |
| `Corrupt { detail }` | `store.corrupt` | no | dialog with "Try recovery" (`sb check --fix` equivalent) |
| `Migration { from, to, detail }` | `store.migration` | no | dialog, document not opened |
| `Marshal(MarshalError)` | `store.marshal` | no | per-cell: value becomes `#UNMARSHALLABLE`; never fails the open |
| `OutOfMemory { bytes }` | `store.oom` | no | bundle rolled back, dialog |
| `ReadOnly` | `store.read_only` | no | toast "Document is read-only" |
| `Io { op, path, source }` | `store.io` | `source.kind() == Interrupted` | dialog |

# `FormulaError` (sheetbase-formula, compile time)

`Syntax { span, message }` (`formula.syntax`), `NoReturn` (`formula.no_return`), `AssignToRec
{ span }` (`formula.assign_rec`), `Unsupported { span, construct }` (`formula.unsupported`,
drives `#PYTHON`), `TooLong { len, max: 65536 }` (`formula.too_long`). None retryable; all shown
inline in the editor. Run-time failures are `Value::Error`, not this enum.

# `ImportError` (sheetbase-import)

`Unreadable { path, source }`, `UnknownFormat { sniffed }`, `TooLarge { bytes, max }`,
`Encoding { detected, position }`, `SheetNotFound { name }`, `ColumnMismatch { expected, found }`,
`UnsupportedGristVersion { found }`. Codes `import.*`, none retryable, all shown in the wizard's
source step with the offending detail.

# `UiError` (sheetbase-ui / app)

`ClipboardUnavailable` (`ui.clipboard`, retryable yes: Wayland focus races), `ClipboardTooLarge
{ bytes }` (`ui.clipboard_limit`, dialog with "copy as text only"), `FontLoad { family }`
(`ui.font`, fallback font, logged), `RenderBackend { detail }` (`ui.render`, fatal at startup
with a dialog offering the glow fallback), `PanicRecovered { message }` (`ui.panic`, error bar
with diagnostics).

# Cell error kinds (`Value::Error`, short codes)

`#TYPE` TypeError, `#VALUE` ValueError, `#KEY` KeyError, `#INDEX` IndexError, `#ATTR`
AttributeError, `#NAME` NameError, `#DIV/0` ZeroDivisionError, `#NUM` OverflowError,
`#INVALID` InvalidTypedValue, `#CIRCULAR` CircularRefError, `#RECURSION`, `#FUEL`, `#SIZE`,
`#NOTSUPPORTED`, `#PYTHON` (uncompiled imported formula), `#UNMARSHALLABLE`, `#INTERNAL`
(recovered panic). The wire form keeps Grist's exception class names in `['E', name, ...]` so
Grist displays them as it would its own.
