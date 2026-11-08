---
type: Component
title: sheetbase-formula
description: L0 crate holding Value, the SFL lexer/parser/compiler/interpreter, the function library, number formats and date handling; no dependency on the document model.
tags: [component, crate, formula]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Purpose

Everything about formulas that does not need a document: the value type, the language, the
functions, formatting of values. Fuzzable and benchmarkable alone.

# Public surface

```rust
pub mod value { pub enum Value; pub struct CellError; pub enum ErrorKind; pub trait StrictEq; }
pub mod types { pub enum ColumnTypeKind; /* the kind without table names, for accepts() */ }
pub mod sfl {
    pub fn compile(source: &str, ctx: &CompileCtx) -> Result<Program, FormulaError>;
    pub fn evaluate(program: &Program, rec: RowId, src: &mut dyn RecordSource, limits: &Limits) -> Value;
    pub fn parse_grist_names(program: &Program) -> Vec<NameRef>;          // for renames
    pub fn complete(source: &str, offset: usize, ctx: &CompileCtx) -> Vec<Completion>;
    pub trait RecordSource;  pub struct Program;  pub struct Limits;  pub struct CompileCtx { tables, columns_of, functions }
}
pub mod functions { pub fn lookup(name: &str) -> Option<&'static FnSpec>; pub fn all() -> &'static [FnSpec]; }
pub mod numfmt { pub struct NumberFormat; pub fn format_value(v: &Value, f: &NumberFormat, locale: &Locale) -> Formatted; pub fn from_grist_options(o: &NumberFormatOptions) -> NumberFormat; }
pub mod date { pub fn format_moment(v: &Value, tokens: &str, tz: TzId) -> SmolStr; pub fn parse_date(s: &str, fmt: Option<&str>) -> Option<Value>; }
pub use thiserror-derived FormulaError;
```

# Dependencies

`smol_str`, `indexmap`, `regex`, `jiff`, `serde` (for `Value` JSON forms), `thiserror`. No
`std::fs`/`net`/`process`. `#![forbid(unsafe_code)]`, `#![deny(clippy::unwrap_used, clippy::expect_used, clippy::panic)]`.

# Size

About 9k lines new (tokenizer 600, parser 1500, compiler 800, interpreter 2500, record objects
800, dates 1200, wrappers 1500) plus about 18k harvested (`numfmt`, `functions`, value compat).

# Requirements carried

REQ-FORMULA-01 to 06, REQ-SEC-02.
