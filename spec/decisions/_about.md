---
type: Overview
title: About the decisions
description: Every contested design decision as an ADR, with the alternatives that lost, why they lost, and who on the panel dissented.
tags: [decisions]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# The panel process

A panel of eight roles argued each one: agentic-AI development, API design, Rust engineering,
software architecture, performance, CLI design, UI design and security. Each ADR records the
proposal, the attacks, the resolution and any dissent that survived. A dissent is not a veto; it
is a flag for the reviewer on sheetbase-spec#1 to weigh.

ADR frontmatter carries `decision_id` (ADR-nnn) and `decision_status`
(`proposed | accepted | superseded | rejected`). A superseding ADR names the one it replaces in
`supersedes`.

# Index by theme

- Licence and repos: ADR-001, ADR-002, ADR-003, ADR-012
- Engine: ADR-004, ADR-005, ADR-006, ADR-009, ADR-015
- Formula language: ADR-007
- Storage: ADR-008
- UI: ADR-010, ADR-011
- Scope: ADR-013, ADR-014, ADR-016
- Cross-cutting: ADR-017
