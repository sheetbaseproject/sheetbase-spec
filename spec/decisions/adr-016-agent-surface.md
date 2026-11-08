---
type: Decision
title: "ADR-016: Agents drive sheetbase through sb serve; the core never calls a network and ships no model"
description: The agentic-AI use case is served by the headless JSON-RPC surface and a stable, documented action vocabulary; no LLM client, API key handling or assistant UI is in the core crates for v1, and a formula assistant, if built, is an external process talking to sb serve.
tags: [decision, agents, security]
status: draft
decision_id: ADR-016
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Context

Grist ships a formula assistant (`formula_prompt.py`, `toggleAssistant` on Mod+K) that calls a
hosted model. The agentic-AI role on the panel wanted sheetbase to be *agent-friendly* from day
one: an agent should be able to open a document, inspect schema, apply actions, read results and
verify them, deterministically and without a GUI.

The security role's position: the engine processes untrusted documents whose formulas are
untrusted code; adding network calls and API keys to the same process widens the blast radius
for every user, including the ones who never asked for an assistant.

# Decision

- Agent surface = `sb serve` (JSON-RPC 2.0 over stdio, [ADR-014](adr-014-no-server-v1.md)) plus
  `sb` subcommands with `--json` output. Every user action Grist defines is callable by name
  with its JSON arguments, and every response includes the resulting `ActionBundle` summary
  (`actionNum`, `stored` doc actions, `undo` length, `retValues`) so an agent can verify what
  happened.
- Schema introspection: `doc.schema` returns tables, columns, types, formulas, dialect flags,
  rules; `doc.describe` returns the same in a compact text form sized for a prompt.
- Determinism: given the same document and the same action list, `sb apply` produces the same
  stored actions and the same cell values (the engine is single-threaded and deterministic;
  `NOW()` is pinned with `--now`).
- Nothing in `sheetbase-core`, `sheetbase-formula`, `sheetbase-store`, `sheetbase-ui` or
  `sheetbase-app` opens a socket. `cargo deny` bans `reqwest`, `hyper`, `ureq`, `tokio-net` in
  those crates. The only process that speaks to the outside is the one a user starts on purpose.
- A formula assistant, if any, is a separate binary or an editor integration that talks to `sb
  serve`, and is out of v1.

# Alternatives

**Built-in assistant like Grist's.** Rejected for v1 on the security argument and because it
needs an account and a key store, which is product surface the desktop app does not otherwise
have.

**MCP server in the core.** gridcraft ships one (`crates/mcp`). The panel sees MCP as one
transport over the same action vocabulary; `sb serve` speaks JSON-RPC which MCP wraps trivially,
so an `sb mcp` subcommand can be added later without touching the engine.

# Consequences

- The action vocabulary is a public API from M2 and is versioned (`doc.apply` takes
  `schemaVersion`), documented in [CLI](../cli/surface.md).
- The spec's own validator, benchmarks and golden tests are driven through `sb`, so the agent
  surface is exercised by CI every day.
