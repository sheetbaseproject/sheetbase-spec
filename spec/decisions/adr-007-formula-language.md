---
type: Decision
title: "ADR-007: A Python-expression-subset formula language, no RustPython in v1"
description: Formulas are written in SFL, a Grist-syntax-compatible subset of Python expressions and small statement bodies, interpreted by a fuel-limited tree walker in sheetbase-formula; gridcraft's Excel engine supplies functions but not syntax; imported Python that the subset cannot compile is preserved and shown as #PYTHON.
tags: [decision, formula, security]
status: draft
decision_id: ADR-007
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-codebuilder
    resource: https://github.com/gristlabs/grist-core/blob/main/sandbox/grist/codebuilder.py
    title: codebuilder.py (make_formula_body, $col rewriting, implicit return, lazy args)
  - id: grist-formulas-help
    resource: https://support.getgrist.com/formulas/
    title: Grist help, Intro to formulas
  - id: gridcraft-functions
    resource: https://github.com/storytold/gridcraft/tree/main/crates/functions
    title: gridcraft-functions (491 functions over Value, MIT OR Apache-2.0)
---

# Context

Grist formulas are Python: `$col` is rewritten to `rec.col`, the last expression is the implicit
return, `IF`/`IFERROR`/`ISERR`/`ISERROR`/`PEEK` get lazy arguments, and the body may contain any
Python statement.[^grist-codebuilder] The help pages teach a small dialect: `$A * $B`,
`$Ref.Field`, `Table.lookupOne(...)`, `len($group)`, `SUM($group.Amount)`, `if/else`
expressions, list comprehensions, string methods, `datetime`.[^grist-formulas-help] Grist runs
this in a gVisor or pyodide sandbox because it is arbitrary code.

Three candidates for a JS-free, Python-free Rust implementation:

1. **RustPython** (0.6.0, MIT): full CPython 3 semantics, 2 to 4 MB of binary, 50 to 100 ms
   interpreter start, a sandbox that relies on removing modules (import hooks can be bypassed in
   subtle ways), `f64`/`BigInt` interop through a `PyObject` layer, and a different error model
   from ours.
2. **gridcraft's engine**: an A1 Excel engine with 491 functions. Its syntax is Excel, its
   references are cells and ranges, its evaluator is bound to `Workbook`.[^gridcraft-functions]
3. **A new language** that is Grist-compatible for the common subset.

# Decision

Option 3 with a precise definition, called SFL (sheetbase formula language). It is specified in
full in [language](../formula/language.md). The one-paragraph version:

- **Syntax**: Python expressions (literals, `$col`, names, attribute access, subscripts and
  slices, calls with positional and keyword arguments, unary/binary/comparison/boolean operators
  with Python precedence and chaining, conditional expressions, list/set/dict displays and
  comprehensions, `lambda`, parenthesised tuples, f-strings without `=`/`!r` conversions) and a
  statement subset for multi-line bodies (`return`, assignment to plain names, augmented
  assignment, `if`/`elif`/`else`, `for ... in` over a finite iterable, `pass`, `try`/`except` with
  a single bare or named handler). No `import`, `def`, `class`, `while`, `global`, `del`,
  `with`, `yield`, `async`, attribute or subscript assignment, walrus, decorators, star-args.
- **Semantics**: Python 3 truthiness, integer division, `None`, string formatting through a
  `%` and `.format` subset, `datetime`/`date`/`timedelta` objects with Grist's `moment`-compatible
  behaviour, `Record`/`RecordSet` objects with Grist's attribute semantics (`$Ref.Field`,
  `$RefList.Field` giving a list, `$group.Amount`), and the Grist function library (`functions/`
  directory, every family) reimplemented in Rust. The function *implementations* for the
  Excel-compatible families (math, stats, text, date, logical, lookup helpers) are harvested from
  gridcraft's `functions` crate and wrapped to Grist names and argument conventions.
- **Evaluation**: a tree-walking interpreter over a resolved AST with a fuel counter (default
  1,000,000 operations per cell), a recursion limit (64 frames), a string length cap (1 MiB), a
  collection size cap (1,000,000 elements), and no host access of any kind. Exceeding a cap
  raises a cell error (`#FUEL`, `#RECURSION`, `#SIZE`), never a panic.
- **Compatibility**: a formula that uses only the subset behaves exactly as in Grist, verified by
  golden tests over the fixture documents. A formula outside the subset is kept verbatim in
  `_grist_Tables_column.formula`, marked in `_sheetbase_Formulas.dialect = 'python'`, and its
  column shows `#PYTHON` with the original text in the error details, with a converter dialog.

# Alternatives

**RustPython embedded.** The agentic role wanted it for full compatibility; the security role
and the performance role killed it for v1: binary size and startup aside, the sandbox is "remove
dangerous builtins and hope", and a formula engine that calls into a GC'd object graph cannot
meet the per-row microsecond budget in [ADR-004](adr-004-column-granularity.md). Kept as the
documented escape hatch (`python` feature, wasm-sandboxed) if migration telemetry shows the
subset misses more than 5 percent of formulas in real documents.

**gridcraft's language.** Wrong model: `$Customer.Name` has no Excel spelling, and users of
`.grist` files would have to rewrite every formula. Rejected. Its *functions* are harvested
([ADR-012](adr-012-gridcraft-harvest.md)).

**Rhai or Starlark.** Rhai (MIT OR Apache-2.0) is a good embedded language but not Python
syntax; Starlark (Apache-2.0, `starlark` 0.14) is a Python *subset* with a Rust implementation
and a real sandbox, which made it the strongest alternative. Lost because Starlark's value model
(frozen values, no `None` semantics quirks, no `datetime`, integers only as big ints, no
operator overloading hooks for `Record`) would need a fork to host Grist records and
`RecordSet` attribute broadcasting, and we would still write the function library. Writing our
own interpreter over our own `Value` is less code than forking Starlark.

# Consequences

- Migration of existing `.grist` documents is measurable: `sb check doc.grist --formulas` reports
  the compile rate per document. The fixture corpus is the first measurement, with a target of
  95 percent of fixture formulas compiling before M3 closes.
- The function library is a long list; it is tracked in [functions](../formula/functions.md)
  with a status per function.
- Dissent (agentic role): without `import re`/`datetime` module semantics, LLM-generated formulas
  copied from Grist's own AI assistant will fail more often. Partially addressed: `re`,
  `datetime`, `math` are available as *built-in namespaces* with the subset of their API Grist
  users actually use (listed in the language spec), without an `import` statement being
  required, and an `import` of exactly those names is accepted and ignored.

[^grist-codebuilder]: codebuilder.py (make_formula_body, $col rewriting, implicit return, lazy args)
[^grist-formulas-help]: Grist help, Intro to formulas
[^gridcraft-functions]: gridcraft-functions (491 functions over Value, MIT OR Apache-2.0)
