---
type: Requirement
title: "Requirements: formula language"
description: "REQ-FORMULA: SFL compatibility with Grist formulas, the function library, the sandbox limits, migration classification and conversion."
tags: [requirements, formula]
status: draft
requirement_id: REQ-FORMULA
priority: must
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

| Id | Requirement | Priority | Verification |
|---|---|---|---|
| REQ-FORMULA-01 | A formula using only the SFL subset evaluates to the same value as in Grist for every fixture document. | must | `sb check` zero differences on compiling fixture formulas |
| REQ-FORMULA-02 | At least 95 percent of formulas in the fixture corpus compile in SFL by the end of M3. | must | `xtask fixtures formula-report` |
| REQ-FORMULA-03 | Every Grist function in `functions/` is implemented or explicitly `#NOTSUPPORTED` with the list in [functions](../formula/functions.md) kept current. | must | registry test comparing against the Grist function list |
| REQ-FORMULA-04 | Evaluation cannot access files, network, environment or process state, and every resource is bounded with a named cell error on overflow. | must | `cargo deny` bans; fuzz; unit tests per cap |
| REQ-FORMULA-05 | An imported formula outside the subset is preserved verbatim, flagged `python`, displayed as `#PYTHON` with the diagnostic, and never silently altered. | must | fixture formula report; UI kittest |
| REQ-FORMULA-06 | Renaming a table or column rewrites every formula that references it, including string arguments of `order_by`/`group_by`. | must | `test_renames.py` port |
| REQ-FORMULA-07 | The compile error for Grist's tested cases carries Grist's message text. | should | `test_codebuilder.py` port |
| REQ-FORMULA-08 | `$A * $B` evaluates in under 1 us, a one-key lookup under 5 us. | should | `sfl_eval_*` benches |
