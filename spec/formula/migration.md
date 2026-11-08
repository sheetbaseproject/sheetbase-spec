---
type: Component Design
title: Formula migration from Grist
description: How each formula in an opened .grist document is classified (compiles in SFL, valid Python both ways, Python only), what the user sees, how conversion works, and the measurement that decides whether the optional Python feature is ever needed.
tags: [formula, migration, grist-compat]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Classification on open

For every `_grist_Tables_column` row with a non-empty `formula`, the import step runs the SFL
compiler and records one row in `_sheetbase_Formulas`:

| `dialect` | `status` | Meaning | Cell display |
|---|---|---|---|
| `both` | `ok` | compiles in SFL and the source is syntactically valid Python 3 using only constructs SFL implements with Python semantics | normal values |
| `sfl` | `ok` | compiles in SFL but uses something not valid Python (an Excel-namespace function such as `XLOOKUP`, or a sheetbase extension) | normal values; "Save as .grist" warns |
| `python` | `unsupported` | does not compile in SFL (uses `def`, `while`, `import` of an unsupported module, attribute assignment, etc.) | `#PYTHON` in every cell, with the compile diagnostic and the original source in the tooltip; the stored last values from the file remain visible greyed in the raw-data view |
| `python` | `error` | compiles in SFL but a documented semantic difference applies (e.g. Python 2 integer division in a very old document, `dict` ordering assumption) | values computed, warning badge on the column |

`sb check doc.grist --formulas` prints the table and a compile rate.

# Conversion

The column menu offers "Convert to sheetbase formula" on a `#PYTHON` column:

1. Mechanical rewrites the converter applies automatically: `import re/datetime/math/json`
   lines dropped; `print(...)` removed; `dict.iteritems()` to `.items()`; `unicode(x)` to
   `str(x)`; `xrange` to `range`; `.has_key(k)` to `k in`; Python 2 `/` on ints flagged.
2. Constructs with a known SFL equivalent are suggested, not applied: a `while` loop with a
   counter becomes a `for i in range(n)` suggestion; a `def helper(...)` body becomes a `lambda`
   suggestion when it is a single expression.
3. Anything else is left for the user with the diagnostic pointing at the offending span.

Converting writes the new formula through `ModifyColumn` (undoable) and flips `dialect` to
`both` or `sfl`.

# Round trip to Grist

"Save as .grist" is allowed when no column has `dialect = 'sfl'` or `status = 'unsupported'`
with a *changed* formula (an untouched `#PYTHON` column keeps its original Python text and Grist
will run it fine). The dialog lists the blocking columns otherwise.

# Measurement

The fixture corpus (118 documents) is the first compile-rate measurement; `xtask fixtures
formula-report` prints per-document rates and the top unsupported constructs. Targets: 95
percent of fixture formulas `ok` by the end of M3; the open question of whether to build the
`python` feature ([open questions](../plan/open-questions.md)) is decided on real-document
telemetry users opt into sending (counts of unsupported constructs only, no formula text).
