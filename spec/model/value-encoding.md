---
type: Component Design
title: Value encoding
description: "How a Value crosses the three boundaries: the Grist wire format (JSON with object codes), SQLite storage (affinities, JSON lists, marshal blobs) and the formula interpreter (rich objects)."
tags: [model, encoding, grist-compat]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-objtypes
    resource: https://github.com/gristlabs/grist-core/blob/main/sandbox/grist/objtypes.py
    title: objtypes.py (encode_object, decode_object, RaisedException, AltText)
  - id: grist-docstorage
    resource: https://github.com/gristlabs/grist-core/blob/main/app/server/lib/DocStorage.ts
    title: DocStorage.ts (_getSqlType, _encodeValue, _decodeValue)
---

# Wire format (what `sb --json`, `sb serve` and the import of Grist data speak)

`CellValue = number | string | boolean | null | [code, ...]`. Codes and their `Value`
mapping:[^grist-objtypes]

| Code | Shape | `Value` | Notes |
|---|---|---|---|
| (none) | `number` | `Int` if the column is Int/Id/Ref and the number is integral, else `Num`; `Date`/`DateTime` when the column type says so | typed columns carry bare numbers |
| (none) | `string` | `Text` | AltText is also a bare string |
| (none) | `boolean` | `Bool` | |
| (none) | `null` | `Null` | |
| `L` | `['L', v...]` | `List`, or `RefList`/ChoiceList when the column type says so | |
| `l` | `['l', value, {column?, raw?}]` | inbound only: resolved through `visibleCol` to `Ref`, else `Text` (AltText) | |
| `O` | `['O', {k: v}]` | `Dict` | |
| `D` | `['D', secs, tz]` | `DateTime` | |
| `d` | `['d', secs]` | `Date` | |
| `R` | `['R', table, id]` | `Ref` | |
| `r` | `['r', table, [ids]]` | `RefList` | |
| `E` | `['E', name, msg?, details?, {u: input}?]` | `Error` | trailing nulls trimmed on encode |
| `C` | `['C']` | `Censored` | ACL |
| `P` | `['P']` | `Pending` | never produced by us; decoded |
| `S` | `['S']` | skip marker in bulk updates: the cell is not written | |
| `U` | `['U', repr]` | `Unmarshallable` | ints outside i64 on decode |
| `V` | `['V', {parent, remote, local}]` | `Dict` with a `versions` tag | conflict marker, preserved |

Rules: `decode` never fails (unknown code becomes `Error { kind: Unmarshallable }`); `encode`
of a typed column emits bare numbers for `Date`/`DateTime`/`Ref` and `['L', ...]` for lists,
and the full `['d', ...]`/`['R', ...]` forms only for `Any` columns or when the caller asks for
`typed` encoding (Grist's `?cellFormat=typed`).

```rust
impl Value {
    pub fn to_grist(&self, ty: &ColumnType, typed: bool) -> serde_json::Value;
    pub fn from_grist(v: &serde_json::Value, ty: &ColumnType, doc: &Document) -> Value;   // resolves ['l', ...]
}
```

# SQLite storage[^grist-docstorage]

| Column type | SQL type | Default |
|---|---|---|
| Bool | `BOOLEAN` | `0` |
| Choice, Text | `TEXT` | `''` |
| ChoiceList, RefList, Attachments | `TEXT` (JSON array) | `NULL` |
| Date | `DATE` | `NULL` |
| DateTime | `DATETIME` | `NULL` |
| Int, Id, Ref | `INTEGER` | `0` |
| Numeric, ManualSortPos, PositionNumber | `NUMERIC` | `0` (ManualSortPos/PositionNumber `1e999`) |
| Any, Blob | `BLOB` | `NULL` |

Encoding on write (`StoreCodec::encode(&Value, SqlAffinity) -> SqlParam`):

- `List` of strings into a ChoiceList column: `JSON.stringify` of the items (no `'L'`).
- `RefList`/Attachments: JSON array of ints.
- Any other `List`, `Dict`, `Error`, `Ref` (in an `Any` column), `Date` in a non-date column:
  **marshal v2 blob** of the Grist-encoded form.
- `Text` whose first char is in `-+ \t\n\r\v0-9.` into a non-TEXT affinity: marshal (dodges
  SQLite's numeric coercion).
- Number into TEXT affinity, `NaN`, `-0.0`, or `0`/`1` into BOOLEAN: marshal.
- `Bool` bare only in BOOLEAN columns.
- `Null`: `NULL`.

Decoding (`StoreCodec::decode(SqlValue, &ColumnType) -> Value`): a blob is `marshal::loads`
then Grist-decoded; a BOOLEAN `0`/`1` is `Bool`; a list column's `'[...'` text is
`JSON.parse` wrapped as a list; everything else is by declared type.

# Marshal codec

`sheetbase-store::marshal` implements Python marshal version 2 for exactly the type codes Grist
emits: `N` None, `T`/`F` bools, `i` int32, `l` long (digit base 2^15), `g` binary float, `s`
bytes, `u` utf-8 str, `t` interned-str (read only), `(` tuple, `[` list, `{` dict, `R` ref
(read only, for interned strings). `dumps` is deterministic and matches Grist's byte output
for the values Grist marshals; proptest compares `loads(dumps(v)) == v` and golden tests compare
`dumps(loads(blob)) == blob` over every blob in the fixture corpus.

```rust
pub fn loads(bytes: &[u8]) -> Result<MarshalValue, MarshalError>;
pub fn dumps(v: &MarshalValue) -> Vec<u8>;
pub enum MarshalError { Truncated { at: usize }, UnknownCode { code: u8, at: usize }, BadUtf8 { at: usize }, Depth { max: u16 } }
```

Depth is capped at 64 and total size at 16 MiB per cell; both are `MarshalError`, decoded into
`Value::Error { kind: Unmarshallable }` rather than failing the load.

# Interpreter objects

Inside a formula `Ref` becomes a `Record` object, `RefList` a `RecordSet`, `Date`/`DateTime`
become `date`/`datetime` objects with Grist's `moment`-compatible methods, `Error` re-raises as
`CellError` with the `(in referenced cell T[r].c)` suffix added when read from another cell, and
AltText raises `InvalidTypedValue` on attribute access. See [language](../formula/language.md).

[^grist-objtypes]: objtypes.py (encode_object, decode_object, RaisedException, AltText)
[^grist-docstorage]: DocStorage.ts (_getSqlType, _encodeValue, _decodeValue)
