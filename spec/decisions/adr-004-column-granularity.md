---
type: Decision
title: "ADR-004: One Causl node per column, carrying a version token, never the data"
description: Formula columns map to one derived node each and data columns to one input node each; node values are tiny version tokens, the rows live in sheetbase's column store, and row-level deltas are handled inside the compute. Per-cell nodes and per-column vector values both fail the 1M-cell arithmetic.
tags: [decision, causl, performance]
status: draft
decision_id: ADR-004
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: causl-cell
    resource: /Users/rom/workspace/causl/causl-core-rs/tools/engine-rs-core/src/cell.rs
    title: InputCell / DerivedCell definitions
  - id: causl-json
    resource: /Users/rom/workspace/causl/causl-core-rs/tools/engine-rs-core/src/json_value.rs
    title: JsonValue enum (Null, Bool, Number(f64), String(SmolStr), Array, Object)
  - id: causl-publish
    resource: /Users/rom/workspace/causl/causl-core-rs/tools/engine-rs-core/src/transition/publish.rs
    title: is_same_value, ECMA SameValue deep compare on every write and recompute
  - id: causl-retention
    resource: /Users/rom/workspace/causl/causl-core-rs/tools/engine-rs-core/docs/retention.md
    title: RetainedRow per commit with full value clones of written inputs
---

# Context

The brief asked the performance role to do the arithmetic for a 1M-cell table (say 50 columns by
20k rows, or 10 columns by 100k rows) and for the dependency cardinality of `lookupRecords`.
Facts about Causl that drive it:[^causl-cell][^causl-json][^causl-publish][^causl-retention]

- `JsonValue` is a boxed enum: `Null | Bool | Number(f64) | String(SmolStr) | Array(Vec) |
  Object(IndexMap)`. About 40 bytes per scalar, `f64` only (no i64, no bytes, no dates).
- `DerivedCell` is about 150 bytes before padding (id, last_value, version, deps SmallVec<[NodeId;
  4]>, observers SmallVec, flags) plus an entry in `dependents`, `registered_at` (BTreeMap) and
  `registration_seed`. Call it 250 bytes per derived node, 120 per input node.
- Every input write and every derived recompute runs `is_same_value`, a deep structural compare,
  O(size of value).
- Every commit pushes a `RetainedRow` whose `delta` clones the full value of every written input;
  the ring holds 1024 commits.
- Recompute cost is about 0.3 microseconds per node in release, plus the compute body.
- A commit costs O(affected set), not O(graph), which is the property we want to keep.

# The arithmetic

**Option A: one node per cell.** 1M cells, say 40 percent formula cells:
- Memory: 400k derived nodes x 250 B = 100 MB, 600k inputs x 120 B = 72 MB, plus `dependents`
  edges (one per formula input reference, say 2 per cell: 800k x 8 B = 6.4 MB), plus BTreeMap
  overhead (two maps x 1M entries x ~48 B = 96 MB). About 275 MB of graph for a 1M-cell table
  whose data is 8 MB as `f64`. Grist itself opens such a document in about 60 MB.
- Time: changing one formula column's text invalidates 20k cells: 20k x 0.3 us = 6 ms engine
  time, acceptable. But a paste into 100k cells of a data column = 100k input writes = one
  `writes` vector of 100k pairs, each deep-compared, plus 100k dependents walks: about 60 ms
  engine time before any formula runs. Grist does this as one `BulkUpdateRecord` and one dirty
  set.
- Node creation at document load: 1M `create_*` calls, each a `BTreeMap` insert: about 500 ms.
  Rejected.

**Option B: one node per column, value = the whole column as `JsonValue::Array`.**
- Memory: a 100k-row numeric column is 100k x 40 B = 4 MB as `JsonValue` (versus 800 KB as
  `Vec<f64>`); 10 columns = 40 MB. Tolerable.
- Time: every write to the column rebuilds and deep-compares a 100k-element array (SameValue is
  O(n)): 100k compares x ~10 ns = 1 ms per column per commit, fine. But a single-cell edit
  copies the 4 MB array into the `writes` vector and into the retention ring; 1024 commits of
  single-cell edits retain up to 4 GB. Retention can be capped at 0, but then `read_at` is gone
  for every node, including the view-model ones that might want it.
- Formulas: the compute for a dependent column receives the *whole* input arrays and has no
  dirty set, so it must recompute all 100k rows for a one-cell change: 100k x (interpreter ~1 us)
  = 100 ms per dependent column per keystroke. That is the end of 60 fps. Rejected.

**Option C (chosen): one node per column, value = version token, rows in the column store.**
- Node value is `{"v": n}` (an object with one `Number`): SameValue compare is O(1), retention
  clones 60 bytes per written node per commit, and the token always changes when data changed,
  so cutoff never wrongly suppresses propagation.
- Memory for the graph: a large document has 50 tables x 20 columns = 1000 column nodes plus
  about 300 lookup-index and summary-helper nodes plus about 2000 view-model nodes: under 4000
  nodes, about 1 MB. Data lives in `ColumnStore` as typed `Vec<T>` (`Vec<f64>` for Numeric,
  `Vec<i64>` for Int and Ref, `Vec<SmolStr>` for Text, bitvec plus null bitmap for Bool, a
  `Vec<u32>` offsets + `Vec<i64>` arena for RefList): a 1M-cell numeric table is 8 MB plus null
  bitmaps.
- Dirty sets: the store keeps, per column node, a `DeltaLog` of `(version, RowSet)` where
  `RowSet` is a roaring-style bitmap (`roaring` crate, MIT OR Apache-2.0) or `All`. A compute
  reads the dirty rows of its dependencies since the version it last saw, maps them through its
  relations ([ADR-005](adr-005-relations-on-causl.md)), recomputes only those rows, and bumps its
  own token.
- Time for a one-cell edit on a 100k-row table with 5 dependent formula columns: 1 input write
  (O(1) compare), 5 derived recomputes x (0.3 us engine + 1 row x 1 us interpreter) = about 10
  microseconds. For a 100k-row paste: 1 write, 5 recomputes x 100k rows x 1 us = 500 ms of
  interpreter, which is the same work Grist does and is what the progress indicator exists for.
- `lookupRecords` cardinality: a formula `Orders.lookupRecords(Customer=$id)` in table
  `Customers` creates dependencies on exactly two nodes: `model:Orders.#lookup#Customer` (the index
  node, itself derived from `model:Orders.Customer`) and `model:Customers.id`. Row-level
  precision comes from the `LookupRelation` (row -> key tuples) the compute maintains, exactly
  as Grist's `_LookupRelation` does. A document with 500 lookup formulas has at most 500 extra
  index nodes and about 1500 edges. Causl's `SmallVec<[NodeId; 4]>` for deps means a formula
  touching more than 4 columns spills to the heap; typical formulas touch 1 to 3.

# Decision

Option C. Precisely:

- `model:{Table}.{Column}` is an input node for a data column and a derived node for a formula
  column. Value type is `{"v": <u64 as f64>}` (versions stay below 2^53 for the life of any
  document; a version is bumped at most once per commit).
- Data never enters Causl. Computes read dependencies' data from `ColumnStore` through a tracked
  `Reader` the facade hands them; tracked reads are what the compute returns as its dep set.
- Grist's `(table, column)` `Node` maps one-to-one onto a Causl node. Grist's `recompute_map`
  rows map onto the store's `DeltaLog`.

# Alternatives not chosen

Options A and B above. Also considered: **per-chunk nodes** (one node per 4096 rows of a
column), which makes dirty sets implicit in the graph. Rejected: `lookupRecords` would depend on
every chunk of the target column (a 100k-row table is 25 chunks, so a lookup has 25 edges and
every relation becomes chunk-aware), and schema actions would create and dispose nodes in bulk.
Marginal win on partial recompute, large loss in simplicity. Noted as a possible later
optimisation for very wide tables.

# Consequences

- The compute callback must be deterministic given the store's contents at the dependencies'
  current versions. It is, because the store is only written by computes of upstream nodes in
  the same commit, in Causl's topological order, and by the staged doc actions before the commit.
- Rollback on `RaceClass` (cycle, compute error) must undo store writes: computes write into a
  `CommitStaging` overlay that is merged only after the commit succeeds
  ([recalc](../model/relations-and-recalc.md)).
- Dissent (Rust engineer): a version token in a `JsonValue::Object` is 60 bytes where a `u64`
  would do; Causl has no integer arm. Accepted as the cost of using Causl unmodified; if
  upstream adds an `I64` arm (the release bridge already fakes one with string markers) we switch.

[^causl-cell]: InputCell / DerivedCell definitions
[^causl-json]: JsonValue enum (Null, Bool, Number(f64), String(SmolStr), Array, Object)
[^causl-publish]: is_same_value, ECMA SameValue deep compare on every write and recompute
[^causl-retention]: RetainedRow per commit with full value clones of written inputs
