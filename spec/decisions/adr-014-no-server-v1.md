---
type: Decision
title: "ADR-014: No server and no collaboration in v1; the headless surface is a local JSON-RPC over stdio"
description: v1 is a single-process desktop app plus a CLI. Multi-user sync is out; the CLI's `sb serve` exposes user actions over JSON-RPC on stdio so agents and tests can drive a document without a window.
tags: [decision, scope, server]
status: draft
decision_id: ADR-014
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Context

Grist's server does five things: hosts documents, authenticates users, applies and broadcasts
action bundles, filters them per user, and runs the sandbox. The brief listed `sheetbase-server`
as a possible crate "if headless/collab is in scope".

# Decision

- Not in v1. Collaboration needs a wire protocol, auth, conflict handling (Grist is
  last-writer-wins on a single authoritative engine) and an operations story. None of that is
  Rust-port work; it is a second product.
- What *is* in v1 is the engine as a library and `sb serve`: JSON-RPC 2.0 over stdio with the
  methods `doc.open`, `doc.close`, `doc.apply` (user actions, returns the bundle summary),
  `doc.fetch` (table data with ACL applied), `doc.subscribe` (pushes `CommitRecord`-shaped
  notifications on stdout), `doc.export`, `formula.eval`, `doc.check`. It is single-client and
  single-document per process. This is enough for agents, for scripted tests and for a future
  server to wrap.
- The action bundle format and the ACL pipeline stay server-ready
  ([ADR-008](adr-008-storage.md), [ADR-013](adr-013-acl-scope.md)).

# Alternatives

**A minimal HTTP server in v1.** Even minimal means TLS, auth and CORS decisions. Rejected.

**No headless surface at all.** The agentic role objected and won: an engine that can only be
driven by clicks cannot be tested end to end without pixels, and the CLI is the cheapest
integration surface we will ever build.

# Consequences

- `sheetbase-cli` is a first-class deliverable from M2 on, not an afterthought.
- The JSON shapes used by `sb serve` are the serde forms of `UserAction`, `DocAction`,
  `ActionBundle` and `TableData`, documented in [CLI](../cli/surface.md).
