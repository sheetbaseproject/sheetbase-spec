---
type: Decision
title: "ADR-009: Undo is inverse doc actions applied as a new commit, not Causl readAt"
description: Every bundle records inverse doc actions as Grist does; undo applies them forward through the normal pipeline as a new Causl commit; Causl's read_at and retention ring are turned off for model nodes because the node values are version tokens.
tags: [decision, engine, undo]
status: draft
decision_id: ADR-009
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Context

Causl keeps a retention ring of input deltas (`RetainedRow`, cap 1024 commits) and offers
`State::read_at(node, time)`; derived history is opt-in. The brief asked whether undo should be
`readAt` or inverse actions.

Under [ADR-004](adr-004-column-granularity.md) a model node's value is `{"v": n}`. `read_at`
would return a past version number, not past data. The data lives in `ColumnStore`.

Grist computes inverse doc actions while applying each doc action (`docactions.py`: a
`BulkUpdateRecord` records the previous values, a `RemoveColumn` records the values and the
`AddColumn` to restore them), stores them in the bundle's `undo` list, and undo sends
`ApplyUndoActions(undo)` which applies them in reverse order through the same engine.

# Decision

- Inverse doc actions, Grist's way, with the same inverse rules per action type (listed in
  [actions and undo](../model/actions-and-undo.md)).
- Undo and redo are user actions (`ApplyUndoActions`, and redo re-applies the original `stored`
  list) and go through the full pipeline: access rules, doc actions, staging, one Causl commit.
  Formula columns recompute from their dependencies; we do not restore formula values from the
  bundle, we recompute them (Grist also recomputes, flushing the results as `calc`-origin
  stored actions).
- Undo stack semantics as Grist's client: a linear stack per document session, grouped by
  `linkId` chains, `otherId` pairing an undo bundle with the bundle it undoes so redo knows what
  to re-apply. Persisted in `_sheetbase_ActionHistory` so undo survives restart.
- Causl retention: `commit_history_cap = 0` on the model graph (no `RetainedRow` at all, no
  `read_at`). View-model nodes do not need history either. If a future feature wants time travel
  of the UI state, it enables retention on a separate `State`.

# Alternatives

**`read_at` on data.** Only works if data is in Causl, which ADR-004 rejected. Even then the
ring is 1024 commits and `read_at` on deriveds is off by default, so undo would be bounded and
would not restore formula outputs. Rejected.

**Snapshot the whole document per action (gridcraft style, COW bands).** gridcraft does this
with `Arc<Workbook>` and 64-row copy-on-write bands, 100 steps or 128 MiB. Attractive for
simplicity. Rejected: inverse actions are what the `.grist` history format stores, Grist's
`undo` lists are what a future server needs, and snapshots of a 1M-cell document are 8 MB each
even with COW when a formula column recomputes fully.

# Consequences

- The inverse of a schema action is exact (Grist's rules are followed to the letter so
  `test_undo.py`, `test_formula_undo.py`, `test_summary_undo.py`, `test_undo_rename.py` port as
  golden tests).
- Undo of a bundle whose redo would now violate an access rule fails with
  `ActionError::Denied { rule, memo }` and leaves the stack intact, as Grist does.
