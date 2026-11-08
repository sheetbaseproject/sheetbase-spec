---
type: Decision
title: "ADR-013: Access rules are parsed, stored and enforced in v1 for an explicit user context, with no identity provider"
description: The full Grist rule grammar and default rule set are implemented in the engine pipeline (actions) and the view model (reads); the user comes from the process (desktop owner, CLI --as-user), not from authentication; user attribute tables and memos are in, share links and SchemaEdit nuances for editors are preserved but not exercised.
tags: [decision, acl, security]
status: draft
decision_id: ADR-013
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Context

Grist enforces access rules only on the server (`GranularAccess.ts`): it pre-checks user
actions, checks each doc action against before/after row snapshots, filters outgoing doc actions
per user and censors cells to `['C']`. The client hides UI but trusts nothing. A desktop
single-user app has no server and exactly one user, which tempts "skip ACL in v1".

Against that: documents carry rules, and a user opening a shared document locally must not see
more than the rules allow if we ever ship the engine headless; the CLI's `sb export --as-user`
is a real use (producing a filtered export for someone), and the test suite must prove the
engine honours rules before a server exists.

# Decision

- `sheetbase-core::acl` implements: the `permissionsText` grammar (`+CRUDS`/`-CRUDS`, `all`,
  `none`), the predicate formula grammar (`user.*`, `rec.*`, `newRec.*`, `and/or/not/in/not in`,
  comparisons, `is`/`is not`, arithmetic, attribute access, literals, `OWNER/EDITOR/VIEWER`),
  parsing to the same `aclFormulaParsed` JSON tree Grist stores (so documents round-trip), the
  default rule set, the `*SPECIAL` pseudo-table (`SchemaEdit`, `AccessRules`, `FullCopies`,
  `SeedRule`), user attribute rules (`userAttributes` JSON, lookup by `charId`, NOCASE for
  Email), `memo`, and locked tables.
- Enforcement points: (1) `check_user_actions` before expansion (special actions denied to
  nuanced users), (2) per doc action during application against before/after rows with
  `direct`/indirect distinction, (3) view-model reads: `view:section:{id}:rows` and
  `view:section:{id}:cells` nodes apply row pruning and cell censoring for the current `User`.
- The `User` struct carries `Name, Email, Access, UserID, UserRef, Origin, LinkKey, SessionID,
  ShareRef, IsLoggedIn` plus attribute records. The desktop app sets `Access = owners`,
  `IsLoggedIn = true`, `Email` from settings or empty. The CLI takes `--as-user
  email=...,access=viewers`.
- Rule editing UI (the Access Rules page) is in v1 as a read-only table in M6 and an editor in
  M7.

# Alternatives

**No ACL in v1.** Rejected for the reasons above; also, enforcement in the view model is what
makes censored cells (`['C']`) render correctly in documents that already have them.

**ACL only in the view model (reads), not on actions.** Half the work. Rejected: `sb apply
--as-user` would silently succeed where Grist would refuse, which breaks the headless contract.

# Consequences

- `ACL-Test.grist` and `BadRules.grist` fixtures become golden tests; `test_acl_formula.py`,
  `test_acl_renames.py`, `test_predicate_formula.py` port as unit tests.
- Rule evaluation runs before the Causl commit and is not a Causl node: it is a precondition,
  not a derived value.
