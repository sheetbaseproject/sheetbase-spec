---
type: Decision
title: "ADR-015: One Value enum shared by formulas, store and UI, with Grist's type lattice"
description: "sheetbase-formula::Value is the single cell value type: Grist's wire codes map onto it losslessly, the store encodes it with Grist's rules, and the UI formats it; Int is i64 with Grist's 32-bit validity check, Numeric is f64, dates are f64 seconds like Grist."
tags: [decision, engine, types]
status: draft
decision_id: ADR-015
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-types
    resource: https://github.com/gristlabs/grist-core/blob/main/app/common/gristTypes.ts
    title: "gristTypes.ts and app/plugin/GristData.ts (GristObjCode: L l O D d S C R r E P U V)"
  - id: grist-usertypes
    resource: https://github.com/gristlabs/grist-core/blob/main/sandbox/grist/usertypes.py
    title: usertypes.py (is_right_type per type, Int is_int_short, dates as float seconds)
---

# Context

Grist has a wire encoding (`CellValue = number | string | boolean | null | [code, ...]`) with
codes for lists, dates, references, errors, censored and pending values,[^grist-types] and a
per-type validity check in the engine (`Int` must fit 32 bits, `Numeric` is float or int,
`Date` is float seconds at midnight UTC, `Bool` is bool or None, `ChoiceList` a tuple of
strings, `RefList` a list of ints).[^grist-usertypes] gridcraft's `Value` is
`Empty | Number(f64) | Text(Arc<str>) | Bool | Error(CellError) | Array(Arc<Array>)`.

# Decision

```rust
/// The one cell value type. Clone is O(1) for everything but Dict and List.
#[derive(Clone, Debug, PartialEq)]
pub enum Value {
    Null,
    Bool(bool),
    Int(i64),                       // Grist Int: stored i64, valid iff -(1<<31) <= v < (1<<31)
    Num(f64),                       // Grist Numeric, PositionNumber, ManualSortPos
    Text(SmolStr),                  // Text, Choice, and AltText (wrong-type raw strings)
    Date(f64),                      // Grist Date: seconds since epoch, midnight UTC
    DateTime(f64, TzId),            // Grist DateTime:tz
    Ref(TableId, RowId),            // ['R', table, id]; RowId 0 is the empty record
    RefList(TableId, Arc<[RowId]>), // ['r', table, [ids]]
    List(Arc<[Value]>),             // ['L', ...] and ChoiceList (all Text)
    Dict(Arc<IndexMap<SmolStr, Value>>), // ['O', {...}]
    Error(Arc<CellError>),          // ['E', name, message?, details?, {u: user_input}?]
    Censored,                       // ['C']
    Pending,                        // ['P']
    Unmarshallable(SmolStr),        // ['U', repr]
    Blob(Arc<[u8]>),                // Blob columns
}

pub struct CellError {
    pub kind: ErrorKind,            // see errors concept: TypeError, ValueError, CircularRef, Python, Fuel, ...
    pub message: SmolStr,
    pub details: Option<SmolStr>,   // traceback-like detail, only when requested
    pub user_input: Option<Box<Value>>, // trigger formula: what the user typed
}
```

- `Value` lives in `sheetbase-formula` (L0) and is used unchanged by `core`, `store`, `ui`.
- Grist wire encoding and decoding (`encode_object`/`decode_object` semantics) is `impl Value {
  fn to_grist(&self) -> serde_json::Value; fn from_grist(v) -> Value }` in `sheetbase-core`;
  `decode` never fails (unknown codes become `Error`), as Grist's does.
- Column type validity (`is_right_type`) is `ColumnType::accepts(&Value) -> bool`; a value that
  does not fit is stored as given and read back as `AltText` semantics (`Value::Text` tagged in
  the column store's `alt` bitmap), exactly as Grist's `AltText` behaves (attribute access on it
  raises `InvalidTypedValue`).
- Numeric equality for change detection uses Grist's `strict_equal` semantics (type and value;
  `1 != 1.0` in Grist), implemented as `Value::strict_eq`.

# Alternatives

**gridcraft's `Value` as is.** No `Int`, no dates, no references, errors are Excel codes.
Rejected as the primary type; its coercion and comparison code (15-significant-digit compare,
`number_to_text`) is harvested into `Value` methods for the Excel-compatible functions.

**Arrow arrays as the value model.** Columnar from the start. Rejected: cells in Grist are
polymorphic (`Any` columns, AltText), and Arrow's union types make that painful; the
`ColumnStore` is typed per column anyway, Arrow is not needed for that.

**`i32` for Int.** Grist checks `is_int_short` but stores Python ints; large ints become
`['U', repr]` on the wire. `i64` storage with the same validity check loses nothing and avoids
a conversion on every SQLite read.

# Consequences

- `size_of::<Value>()` is 24 bytes (`DateTime(f64, TzId)` and `Ref(TableId, RowId)` set the
  payload at 16). `ColumnStore` does not store `Value` per cell; it stores typed vectors and
  materialises `Value` on read. The `Any` column type is the exception and stores `Vec<Value>`.
- `TzId` is an interned index into the document's timezone table (`chrono-tz` names); `Date`
  arithmetic uses `jiff` (Unlicense OR MIT) for correctness of civil time, with Grist's
  `moment`-compatible formatting tokens implemented over it.

[^grist-types]: gristTypes.ts and app/plugin/GristData.ts (GristObjCode: L l O D d S C R r E P U V)
[^grist-usertypes]: usertypes.py (is_right_type per type, Int is_int_short, dates as float seconds)
