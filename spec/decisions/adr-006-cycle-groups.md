---
type: Decision
title: "ADR-006: Column-level cycles collapse into a cycle group node evaluated cell by cell"
description: When Causl reports CycleClosed for a set of formula columns, sheetbase merges that strongly connected component into one derived node whose compute runs Grist's lazy per-cell evaluator with cell locks, so row-acyclic formulas keep working and true cycles become per-cell CircularRefError.
tags: [decision, causl, engine]
status: draft
decision_id: ADR-006
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Context

Grist allows formulas that are cyclic at column level but acyclic at cell level. The canonical
case is a running total: `Balance = $Prev.Balance + $Amount` where `Prev` is a Ref to the previous
row of the same table. Column `Balance` depends on column `Balance`. Grist handles it with
`OrderError` and `_locked_cells`: a cell that needs a not-yet-computed cell suspends, the needed
cell is computed first, and a cell that needs itself gets `CircularRefError`.

Causl detects cycles at commit time over the affected set and rejects the whole commit with
`RaceClass::CycleClosed { path }`. There is no per-row notion, so a self-dependent column is a
cycle to Causl, always.

# Decision

- At compile time (when a formula's static reads are known) and at commit time (when a dynamic
  read closes a cycle), `sheetbase-core` computes the strongly connected components of the
  column-level graph with Tarjan's algorithm over its own edge mirror.
- Every SCC with more than one node, or a single node with a self edge, is represented in Causl
  by **one derived node** `model:{Table}.#cycle#{n}` whose compute evaluates all member columns
  together using the Grist algorithm: a work queue of `(column, row)` cells, a lock set, lazy
  evaluation on read of an uncomputed member cell, and `CircularRefError` stored into any cell
  reached while locked. The member columns' own nodes become plain inputs written by the group
  compute (so downstream formulas still depend on `model:T.Balance`, not on the group).
- When the SCC dissolves (a formula is edited), the group node is disposed and the members become
  ordinary derived nodes again. All of this happens before the Causl commit, in the schema phase
  of applying a bundle, so Causl itself never sees a cycle from formulas. If it does anyway
  (dynamic read discovered mid-commit), the commit is rejected, the SCC is recomputed, and the
  bundle is re-applied once; a second rejection surfaces as `EngineError::CycleUnresolved` and
  the user action fails cleanly.

# Alternatives

**Reject cyclic formulas outright (`#CIRCULAR` in every cell of the column).** Simplest and what
a naive Causl port would do. Rejected because `PREVIOUS()`, `$Prev.X`, `RANK` over `lookupRecords`
on the same table and summary-of-self patterns are common in real Grist documents; the
118 fixtures include them (`test_prevnext.py` covers the cases).

**Fork Causl to support per-row cycles.** No; see [ADR-005](adr-005-relations-on-causl.md).

**Iterative calculation (Excel style).** Wrong semantics for Grist documents, and non-deterministic
with a step cap. Rejected.

# Consequences

- The group compute is the one place where the Grist-style lazy evaluator lives; everywhere
  else evaluation is a straight loop over dirty rows. Both share the interpreter.
- Group computes are O(member cells) on a full invalidation but still use dirty sets on
  incremental changes (the group has relations to its external dependencies like any node).
- A cycle group's version token bumps when any member changed; downstream columns read the
  member nodes, whose tokens the group compute bumps individually, so there is no over-invalidation.
