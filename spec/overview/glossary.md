---
type: Reference
title: Glossary
description: Grist, Causl and sheetbase terms side by side, so the rest of the spec can use them without re-explaining.
tags: [overview, glossary]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

| Term | Meaning here | Grist equivalent | Causl equivalent |
|---|---|---|---|
| Document | One SQLite file, all tables, metadata, history | `.grist` file, `ActiveDoc` | one `State` |
| Table | Named collection of records with a schema | `_grist_Tables` row, user table | a group of nodes `model:T.*` |
| Column | Typed field of a table, data or formula | `_grist_Tables_column` row | one node per column |
| Record | A row; `id` is a positive integer, 0 is the empty record | `Record` in `records.py` | not a node (rows live in the column store) |
| Column store | sheetbase's in-memory columnar storage per table (`Vec` per column indexed by row id) | `BaseColumn._data` list | none; Causl values are version tokens |
| User action | What the client asks for (`AddRecord`, `UpdateRecord`, `AddColumn`, ...) | `@useraction` in `useractions.py` | the intent string of a commit |
| Doc action | A primitive change the engine applied (`BulkUpdateRecord`, `AddColumn`, ...) | `actions.py` namedtuples, `DocActions.ts` | the `writes` of a `CommitWithValues` |
| Bundle | All doc actions from one user action request plus their inverses | `LocalActionBundle` | one `CommitRecord` (`time`, `intent`, `changed_nodes`) |
| Relation | A mapping from rows of a depending column to rows of a dependency column | `relation.py` (Identity, Reference, lookup, summary group) | none; relations live in `sheetbase-core` and run inside computes |
| Dirty set | Row ids of a column that changed in a commit | `recompute_map` entries | none (kept in the column store's delta table, keyed by node version) |
| Version token | The `JsonValue` a sheetbase column node carries: `{"v": n}` | none | the node value, compared by SameValue |
| Lookup index | Derived node mapping key tuples to row sets for `lookupRecords` | `LookupMapColumn` `#lookup#Col1:Col2` | derived node `model:T.#lookup#...` |
| Summary helper | Derived node mapping each source row to its summary group row | `#summary#SummaryTableId` helper column | derived node |
| Cycle group | A set of formula columns that reference each other at column level and are evaluated together cell by cell | `OrderError` + `_locked_cells` | a single derived node standing in for the SCC |
| Section | A widget on a page over one table | `_grist_Views_section` | `view:section:{id}:*` nodes |
| Field | A column shown in a section with its own options | `_grist_Views_section_field` | part of the section's node group |
| Page | A tree node in the left panel showing a view | `_grist_Pages` + `_grist_Views` | `view:page:{id}` |
| Linking | Section A's cursor or selection filters section B | `LinkingState.ts` | `view:section:{id}:linkfilter` derived from the source section's cursor node |
| Access rule | Resource (table, columns) + predicate + permissions | `_grist_ACLRules` / `_grist_ACLResources` | evaluated before the commit, never inside |
| Commit | Atomic application of writes plus glitch-free settle of every dependent node | n/a | `Action::CommitWithValues` through `transition_phased_in_place_with_callbacks` |
| Compute | The pure function a derived node runs | formula method on the generated table class | `ComputeCallback::compute` |
| Facade | `sheetbase-graph::Graph`, the trait the engine talks to | n/a | implemented by `CauslGraph` and `ReferenceGraph` |
| SFL | The sheetbase formula language, a Python-expression subset | Python formulas | n/a |
| `#PYTHON` | Cell error for an imported formula that SFL cannot compile | n/a | n/a |
