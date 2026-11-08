---
type: Requirement
title: "Requirements: access rules and views"
description: "REQ-ACL and REQ-VIEW: rule grammar and enforcement for an explicit user, and the view model (pages, sections, fields, sort, filter, linking, styles)."
tags: [requirements, acl, views]
status: draft
requirement_id: REQ-ACL/REQ-VIEW
priority: must
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

| Id | Requirement | Priority | Verification |
|---|---|---|---|
| REQ-ACL-01 | The full `permissionsText` and predicate grammars parse, round-trip to Grist's `aclFormulaParsed` JSON, and evaluate with Grist's semantics including user attribute tables and memos. | must | `test_acl_formula.py`, `test_predicate_formula.py`, `ACL-Test.grist` |
| REQ-ACL-02 | For a given `User`, denied actions fail with `Denied` and unreadable rows and cells are pruned or censored in every view and in `sb export`/`doc.fetch`. | must | `ACL-Test.grist` with `--as-user` cases matching Grist's behaviour |
| REQ-ACL-03 | A malformed rule denies rather than allows and surfaces `BadRule`. | must | `BadRules.grist` |
| REQ-VIEW-01 | Every section type is rendered (`record`, `single`, `detail`, `chart`) or shown as a preserving placeholder (`custom`, `form`); section options, sort specs, saved and unsaved filters, pinned filters, frozen columns, row heights, card layouts are honoured. | must | fixture walkthrough: `GridWithAllFields`, `CardView`, `FieldSettings`, `FilterTest`, `SortDates`, `Pages` |
| REQ-VIEW-02 | All seven Grist link types filter or move the cursor as Grist does, including cursor cycles and new-row default values. | must | `SelectBy*`, `LinkChain`, `FilterLinkChain`, `CursorWithRefLists1` fixtures |
| REQ-VIEW-03 | View-model derivations are Causl `view:` nodes recomputed in the same commit as the data change, so one frame after a commit shows a consistent page. | must | kittest: edit a linked source and assert the target's rows in the next frame |
| REQ-VIEW-04 | Conditional formatting on cells, columns and rows resolves per Grist's rule order. | must | `SummaryRulesBug.grist`, `test_rules*.py` |
