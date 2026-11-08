---
type: Reference
title: Function library
description: Every function Grist's functions/ package exposes, grouped as Grist groups them, with where the sheetbase implementation comes from (harvested from gridcraft-functions, new, or not in v1) and the Grist-specific argument conventions kept.
tags: [formula, functions, gridcraft]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-functions
    resource: https://github.com/gristlabs/grist-core/tree/main/sandbox/grist/functions
    title: sandbox/grist/functions (date, info, logical, lookup, math, schedule, stats, text, prevnext)
  - id: gridcraft-functions
    resource: https://github.com/storytold/gridcraft/tree/main/crates/functions/src
    title: gridcraft-functions (math.rs, stat.rs, text.rs, date.rs, lookup.rs, info.rs, financial.rs, engineering.rs, database.rs, dynamic.rs)
---

# Conventions

Grist functions take Python values and return Python values; many accept lists and
`RecordSet` attribute results (`SUM($group.Amount)`). The harvested gridcraft implementations
take `&[Arg]` of `Value` with array lifting. The wrapper layer (`sheetbase-formula::functions::grist`)
flattens nested lists and `RecordSet` attribute lists into gridcraft `Array`s, maps `Int`/`Num`
to `Number(f64)` and back (restoring `Int` where Grist returns an int), maps our `Error` to
gridcraft `CellError` and back, and keeps Grist's argument order where the two differ. Date
functions convert between Grist `date`/`datetime` objects and Excel serials at the boundary
(gridcraft `core/date.rs`, 1900 system, `serial_from_unix_ms`).

Status: **H** harvested from gridcraft with a wrapper; **N** new Rust code; **G** Grist-only
semantics reimplemented from Grist's documented behaviour; **X** not in v1 (returns
`#NOTSUPPORTED`).

# date (`functions/date.py`)[^grist-functions]

| Function | Status | Notes |
|---|---|---|
| DATE, DATEADD, DATEDIF, DATEVALUE, DAY, DAYS, EDATE, EOMONTH, HOUR, ISOWEEKNUM, MINUTE, MONTH, NOW, SECOND, TODAY, WEEKDAY, WEEKNUM, YEAR, YEARFRAC | H | gridcraft `date.rs` has all but DATEADD; DATEADD is N (Grist-specific `years/months/days/weeks` kwargs) |
| DTIME | G | Grist's `DTIME(value, tz=None)` parsing |
| NETWORKDAYS | H | |
| MOONPHASE | G | ported from Grist's formula (astronomical algorithm, public) |
| XL_TO_DATE, DATE_TO_XL | N | trivial serial conversion |

# info (`functions/info.py`)

| Function | Status | Notes |
|---|---|---|
| ISBLANK, ISERR, ISERROR, ISLOGICAL, ISNA, ISNONTEXT, ISNUMBER, ISTEXT, N, NA, TYPE | H | ISERR/ISERROR take lazy args (compile pipeline) |
| ISREF, ISREFLIST | G | `isinstance` of `Record`/`RecordSet` |
| ISEMAIL, ISURL | G | Grist regexes ported |
| CELL | X | A1 cell info has no meaning |
| PEEK | G | evaluate the lazy arg without registering dependencies |
| RECORD | G | `RECORD(rec_or_recordset, dates_as_iso=False, expand_refs=0)` to dict |
| REQUEST | X | I/O |

# logical (`functions/logical.py`)

AND, OR, NOT, IF (lazy), IFERROR (lazy), TRUE, FALSE: H.

# lookup (`functions/lookup.py`)

| Function | Status | Notes |
|---|---|---|
| VLOOKUP | G | Grist's `VLOOKUP(table, **field_value_pairs)` is record-based, not range-based |
| CONTAINS | G | key wrapper for lookups (`match_empty`) |
| SELF_HYPERLINK | G | builds a URL to the current record; needs `doc_url` from settings |
| HYPERLINK | H | returns the Grist `label url` text form |
| ADDRESS, CHOOSE, COLUMN, COLUMNS, GETPIVOTDATA, HLOOKUP, INDEX, INDIRECT, LOOKUP, MATCH, OFFSET, ROW, ROWS | X | A1-model functions; Grist marks most of them unimplemented too |

# math (`functions/math.py`)

ABS ACOS ACOSH ARABIC ASIN ASINH ATAN ATAN2 ATANH CEILING COMBIN COS COSH DEGREES EVEN EXP FACT
FACTDOUBLE FLOOR GCD INT LCM LN LOG LOG10 MOD MROUND MULTINOMIAL ODD PI POWER PRODUCT QUOTIENT
RADIANS RAND RANDBETWEEN ROMAN ROUND ROUNDDOWN ROUNDUP SERIESSUM SIGN SIN SINH SQRT SQRTPI
SUBTOTAL SUM SUMIF SUMIFS SUMPRODUCT SUMSQ TAN TANH TRUNC: H (SUBTOTAL is G over lists).
UUID: G (volatile, per-commit seeded). NUM: G (Grist's `NUM(value)` coercion).

# stats (`functions/stats.py`)

AVEDEV AVERAGE AVERAGEA AVERAGEIF AVERAGEIFS BINOM_DIST BINOM_INV CHISQ_DIST CHISQ_DIST_RT
CHISQ_INV CHISQ_INV_RT CHISQ_TEST CONFIDENCE_NORM CONFIDENCE_T CORREL COUNT COUNTA COUNTBLANK
COUNTIF COUNTIFS COVARIANCE_P COVARIANCE_S DEVSQ EXPON_DIST F_DIST F_DIST_RT F_INV F_INV_RT
F_TEST FISHER FISHERINV FORECAST GAMMA GAMMA_DIST GAMMA_INV GAMMALN GEOMEAN HARMEAN HYPGEOM_DIST
INTERCEPT KURT LARGE LOGNORM_DIST LOGNORM_INV MAX MAXA MEDIAN MIN MINA MODE_MULT MODE_SNGL
NEGBINOM_DIST NORM_DIST NORM_INV NORM_S_DIST NORM_S_INV PEARSON PERCENTILE PERCENTILE_EXC
PERCENTILE_INC PERCENTRANK PERCENTRANK_EXC PERCENTRANK_INC PERMUT PHI POISSON_DIST PROB
QUARTILE QUARTILE_EXC QUARTILE_INC RANK RANK_AVG RANK_EQ RSQ SKEW SKEW_P SLOPE SMALL STANDARDIZE
STDEV STDEVA STDEVP STDEVPA STEYX T_DIST T_DIST_2T T_DIST_RT T_INV T_INV_2T T_TEST TRIMMEAN VAR
VARA VARP VARPA WEIBULL_DIST Z_TEST: H (Grist spells dots as underscores; the wrapper maps
`NORM_DIST` to gridcraft `NORM.DIST`). MEDIAN of dates and `MAX`/`MIN` over dates keep the date
type: G.

# text (`functions/text.py`)

CHAR CLEAN CODE CONCAT CONCATENATE DOLLAR EXACT FIND FIXED LEFT LEN LOWER MID PROPER REPLACE REPT
RIGHT SEARCH SUBSTITUTE T TRIM UPPER VALUE: H. REGEXEXTRACT REGEXMATCH REGEXREPLACE: H
(gridcraft has REGEXEXTRACT/REGEXREPLACE/REGEXTEST; REGEXMATCH maps to REGEXTEST; the `regex`
crate guarantees linear time, Python regex syntax differences documented). PHONE_FORMAT: G
(Grist's E.164 formatter, ported). TEXT: H (gridcraft `numfmt::text_function`). TASTEME: G
(Grist's joke function; kept for fixture compatibility). STRIP, UNICODE, UNICHAR: H.

# schedule (`functions/schedule.py`)

SCHEDULE: G (Grist's recurrence-string parser, ported with its tests).

# prevnext (`functions/prevnext.py`)

PREVIOUS, NEXT, RANK: G, implemented over sorted lookup indexes with the `Relation::Lookup`
machinery; these are the functions that most often create column-level self-cycles, handled by
[ADR-006](../decisions/adr-006-cycle-groups.md).

# Not Grist, available anyway

The 491 gridcraft functions not listed above (financial, engineering, database, dynamic arrays
over lists) are registered under their Excel names in a `functions::excel` namespace reachable
as plain names when they do not collide with a Grist name; `FILTER`, `SORT`, `UNIQUE`,
`SEQUENCE` operate on lists. This is a convenience, not a compatibility promise, and
`sb check --strict-grist` warns on their use.

# Tests

Every H function keeps gridcraft's tests (ported to our `Value`); every G function ports the
corresponding Grist `test_functions.py`/doctest examples from the function docstrings (Grist's
docstrings contain `>>>` examples, which are extracted into a table-driven test by
`xtask fixtures grist-doctests`).

[^grist-functions]: sandbox/grist/functions (date, info, logical, lookup, math, schedule, stats, text, prevnext)
[^gridcraft-functions]: gridcraft-functions (math.rs, stat.rs, text.rs, date.rs, lookup.rs, info.rs, financial.rs, engineering.rs, database.rs, dynamic.rs)
