---
type: Component Design
title: Formula language (SFL)
description: The grammar, the semantics, the compile pipeline ($col rewriting, implicit return, lazy arguments) and the interpreter of the sheetbase formula language, a Grist-compatible Python-expression subset.
tags: [formula, language, rust]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-codebuilder
    resource: https://github.com/gristlabs/grist-core/blob/main/sandbox/grist/codebuilder.py
    title: codebuilder.py (make_formula_body, DOLLAR rewriting, LAZY_ARG_FUNCTIONS, implicit return)
  - id: grist-records
    resource: https://github.com/gristlabs/grist-core/blob/main/sandbox/grist/records.py
    title: records.py (Record, RecordSet attribute semantics)
  - id: grist-formulas-help
    resource: https://support.getgrist.com/formulas/
    title: Grist help, Intro to formulas
---

# Grammar (EBNF, Python tokens)

```
program      := NEWLINE* stmt+                            -- a formula body; a single expression is the common case
stmt         := simple_stmt NEWLINE | compound_stmt
simple_stmt  := expr                                      -- implicit return if it is the last statement
              | 'return' [expr]
              | NAME '=' expr                             -- assignment to a plain local name only
              | NAME augop expr                           -- += -= *= /= //= %= **=
              | 'pass'
              | 'import' dotted_name (',' dotted_name)*   -- accepted and ignored for: re datetime math json (migration aid)
              | 'from' dotted_name 'import' ...           -- same
compound_stmt:= 'if' expr ':' block ('elif' expr ':' block)* ['else' ':' block]
              | 'for' NAME [',' NAME]* 'in' expr ':' block ['else' ':' block]
              | 'try' ':' block ('except' [NAME ['as' NAME]] ':' block)+
block        := NEWLINE INDENT stmt+ DEDENT | simple_stmt NEWLINE
expr         := lambda | ternary
lambda       := 'lambda' [params] ':' expr
ternary      := or_test ['if' or_test 'else' expr]
or_test      := and_test ('or' and_test)*
and_test     := not_test ('and' not_test)*
not_test     := 'not' not_test | comparison
comparison   := arith (comp_op arith)*                    -- chained, Python semantics
comp_op      := '<' | '>' | '==' | '>=' | '<=' | '!=' | 'in' | 'not' 'in' | 'is' | 'is' 'not'
arith        := term (('+' | '-') term)*
term         := factor (('*' | '/' | '//' | '%') factor)*
factor       := ('+' | '-' | '~') factor | power
power        := primary ['**' factor]
primary      := atom trailer*
trailer      := '(' [args] ')' | '[' subscript ']' | '.' NAME
subscript    := expr | [expr] ':' [expr] [':' [expr]]
atom         := NAME | '$' NAME | NUMBER | STRING+ | FSTRING | 'None' | 'True' | 'False'
              | '(' [expr | tuple | genexp] ')' | '[' [list | listcomp] ']' | '{' [dict | set | dictcomp | setcomp] '}'
args         := arg (',' arg)* ; arg := expr | NAME '=' expr          -- no *args / **kwargs
comp_for     := 'for' targets 'in' or_test ['if' or_test]*
```

Not in the language, by decision ([ADR-007](../decisions/adr-007-formula-language.md)):
`def`, `class`, `while`, `with`, `global`, `nonlocal`, `del`, `yield`, `await`, `async`,
decorators, walrus, star-args, attribute or subscript assignment, tuple unpacking in assignment
(allowed only in `for` targets), `print`, `exec`, `eval`, `open`, `__dunder__` names.

# Compile pipeline (`codebuilder.py` ported)[^grist-codebuilder]

1. Dedent the source.
2. Tokenise with a Python 3 tokenizer (our own, ~600 lines; INDENT/DEDENT, string prefixes
   `r`, `f`, `b`, `u`, implicit concatenation, numeric literals incl. `1_000`, `0x`, `1e3`).
3. `$name` tokens become `rec.name` attribute reads at the AST level (the lexer emits a
   `Dollar(name)` token; no textual rewriting, so column positions in errors stay right).
4. Lazy arguments: calls to `IF`, `ISERR`, `ISERROR`, `IFERROR`, `PEEK` wrap each argument in a
   thunk, as Grist's `LAZY_ARG_FUNCTIONS` does.
5. Implicit return: if the last statement is an expression it becomes `return expr`; a body with
   no `return` anywhere and a non-expression last statement is
   `CompileError::NoReturn` (Grist's "No `return` statement, and the last line isn't an
   expression.").
6. Resolve names: `rec`, `table`, `value` (trigger formulas), `user` (trigger formulas), table
   names from the document schema, function names from the library, the three built-in
   namespaces `re`, `datetime`, `math` (plus `json` with `loads`/`dumps`), locals from
   assignments and comprehension targets. An unresolved name compiles to a runtime
   `NameError`-kind cell error (Grist does the same at run time), but also registers a dependency
   on `model:{T}.#schema` so adding a column with that name recomputes.
7. Reject: assignment to `rec` or `rec.x` (Grist's astroid tip), `$x = ...`.
8. Produce `Program { ops: Vec<Op>, consts, spans, static_reads: Vec<ColumnName> }`: a
   resolved tree (not bytecode; a tree walker over `Op` enum nodes with pre-resolved slot
   indices for locals).

`parse_grist_names(program)` returns every `(table, column)` reference including those in
`order_by`/`group_by` string arguments, so renames rewrite formulas as Grist's `renames` logic
does (`test_renames.py`, `test_rename_relations.py` are the golden suites).

# Semantics

- **Values**: `Value` from [ADR-015](../decisions/adr-015-value-model.md). `Int` and `Num` follow
  Python 3: `/` is true division to `Num`, `//` floors, `%` has the divisor's sign, `**` of ints
  is `Int` unless negative exponent, overflow of `Int` promotes to `Num` with a `#NUM` error if
  non-finite (Grist would give a Python long; we store `['U', repr]` on the wire for the rare
  case and the cell shows the digits).
- **Truthiness**: Python's (`0`, `0.0`, `''`, `None`, empty list/dict/set, `Record` with id 0,
  empty `RecordSet` are false).
- **Strings**: `str` methods `upper lower strip lstrip rstrip split rsplit join replace
  startswith endswith find rfind index count format isdigit isalpha isalnum isspace isupper
  islower title capitalize zfill ljust rjust center partition rpartition splitlines encode`,
  `%` formatting (`%s %d %f %.2f %x %r %%`), `.format` with positional and named fields and
  format specs, f-strings with format specs (no `!r`, no `=`). Slicing with negative indices.
- **Collections**: `list` (`append extend insert pop remove index count sort reverse`), `tuple`,
  `dict` (`get keys values items setdefault update pop`), `set` (`add remove discard union
  intersection difference issubset`), builtins `len sum min max sorted reversed enumerate zip
  range any all abs round int float str bool list tuple dict set map filter isinstance type
  repr divmod pow hash` (`hash` of our values, stable per process). Comprehensions bind their
  own scope.
- **Records** (`records.py` semantics):[^grist-records] `rec.Col` reads the cell with a tracked
  dependency; `rec.id`; `int(rec)` is the id; `rec` is falsy iff id 0; `$Ref.Col` follows a
  reference (`Relation::Reference`); `$RefList.Col` gives a `list`, or a merged `RecordSet` if
  every value is a `Record`; `RecordSet` supports `len`, iteration, `in`, `[i]`, `.get_one()`,
  `.find.lt/le/gt/ge/eq/previous/next/rank` on sorted lookups, attribute access broadcasting;
  reading a missing column raises `AttributeError`-kind error and depends on `#schema`; reading
  an error cell re-raises it with the `(in referenced cell ...)` suffix; reading AltText and
  then an attribute raises `InvalidTypedValue`.
- **Tables**: `Table.lookupRecords(**kw)`, `lookupOne`, `.all`, `Table.Record`, `len(Table.all)`
  fast path; `order_by="-Col"` strings and tuples; `CONTAINS(value, match_empty=...)` key wrapper.
  `lookupOrAddDerived` is not in v1 formulas (`#NOTSUPPORTED`).
- **Dates**: `datetime.date`, `datetime.datetime`, `datetime.timedelta` with the methods Grist
  users use (`year month day hour minute second weekday isoweekday strftime isoformat replace
  date time timestamp`, arithmetic with `timedelta`, comparison), `datetime.datetime.now()`
  depends on `model:#now`. Grist's `moment`-compatible behaviour: a `Date` cell reads as a
  `date`, a `DateTime` cell as a tz-aware `datetime` in the column's zone (`jiff` underneath).
- **Errors**: Python exception names map to `ErrorKind`: `TypeError`, `ValueError`, `KeyError`,
  `IndexError`, `AttributeError`, `NameError`, `ZeroDivisionError`, `OverflowError`,
  `InvalidTypedValue`, `CircularRefError`, `RecursionError`, plus ours `FuelExceeded`,
  `SizeExceeded`, `NotSupported`, `Python` (migration). `try/except NAME` catches by kind
  (`except Exception` catches all), `raise` is not available (an uncaught error is produced by
  the operation itself).
- **Determinism**: no `random` module in v1 (`RAND()` and `UUID()` are volatile functions
  implemented with a per-commit seeded generator so recompute is reproducible within a commit;
  they depend on `model:#now`). No `time.time()`. Dict and set iteration order is insertion
  order.

# Interpreter

```rust
pub struct Program { ops: Vec<Op>, consts: Vec<Value>, spans: Vec<Span>, pub static_reads: Vec<ColumnName>, pub source: Arc<str> }
pub struct Limits { pub fuel: u64 /* 1_000_000 */, pub depth: u16 /* 64 */, pub max_string: usize /* 1 MiB */, pub max_collection: usize /* 1_000_000 */ }

pub trait RecordSource {          // implemented by sheetbase-core; the interpreter never sees ColumnStore
    fn read_cell(&mut self, table: TableName, col: &ColumnName, row: RowId, via: &Relation) -> Result<Value, CellError>;
    fn lookup(&mut self, table: TableName, keys: &[(ColumnName, KeyMode, Value)], order_by: Option<&SortSpec>) -> Result<Arc<[RowId]>, CellError>;
    fn all_rows(&mut self, table: TableName) -> Arc<[RowId]>;
    fn column_exists(&mut self, table: TableName, col: &ColumnName) -> bool;
    fn now(&self) -> f64;
    fn user(&self) -> Option<&User>;
}

pub fn evaluate(program: &Program, rec: RowId, src: &mut dyn RecordSource, limits: &Limits) -> Value;   // never panics; errors are Values
```

Tree walking over resolved `Op`s with a `SmallVec<[Value; 8]>` local frame; fuel decremented per
`Op`; depth per call (lambda) frame. Target cost: 1 us for `$A * $B`, 5 us for a one-key lookup
plus `len`, measured by `sheetbase-formula/benches/eval.rs` and gated in CI
([performance budgets](../quality/performance-budgets.md)).

# Autocomplete and errors for the editor

`Program::describe_at(offset) -> Completion` gives the UI column, table and function names in
scope; `CompileError { kind, span, message }` carries the span so the editor underlines it, and
`Formula::from_source` returns `Result<Program, CompileError>` with Grist's exact messages for
the cases its tests check (`test_codebuilder.py`).

[^grist-codebuilder]: codebuilder.py (make_formula_body, DOLLAR rewriting, LAZY_ARG_FUNCTIONS, implicit return)
[^grist-records]: records.py (Record, RecordSet attribute semantics)
[^grist-formulas-help]: Grist help, Intro to formulas
