---
type: Component
title: sheetbase-spec (this bundle)
description: "The specification repo: the OKF bundle under spec/, the validator under tools/, and the rules for changing it."
tags: [component, spec, okf]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Rules

- Every concept has frontmatter with `type`, `title`, `description`, `tags`, `status`,
  `generated`. Decisions carry `decision_id`/`decision_status`; requirements carry
  `requirement_id`/`priority`.
- `index.md` files are generated (`python3 -I tools/okf_check.py spec --write-indexes`) and
  committed; the validator fails if they drift.
- Links are bundle-relative or relative and must resolve; the validator fails on broken links
  (stricter than OKF, which tolerates them).
- A change to a decision is a new ADR with `supersedes`, never an edit that changes the meaning
  of an accepted one; typo fixes are fine.
- `log.md` gets an entry per PR.
- `status: draft` flips to `stable` when the review on the PR that introduced the concept lands.

# Validator

`tools/okf_check.py` (stdlib + PyYAML, which the reference parser also requires). Runs in CI
on every PR via a one-line workflow; locally with `python3 -I`.

# Conformance

OKF v0.2 section 11: every non-reserved `.md` has parseable frontmatter with a non-empty `type`;
`index.md` and `log.md` follow sections 8 and 9. Types used here (`Overview`, `Decision`,
`Requirement`, `Component`, `Component Design`, `Reference`, `Plan`) are producer-defined, as the
spec allows.
