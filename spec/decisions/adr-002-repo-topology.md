---
type: Decision
title: "ADR-002: Three repos, one cargo workspace"
description: The org holds a spec repo, one cargo workspace with eight crates, and the Causl mirror; per-crate repos were rejected as coordination cost without a release-cadence benefit.
tags: [decision, topology]
status: draft
decision_id: ADR-002
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Context

The brief suggested up to nine repos (core, formula, graph, ui, app, server, spec, import, and
more). The architecture role pushed for fewer.

# Decision

- `sheetbase-spec`: the OKF bundle.
- `sheetbase`: one cargo workspace, eight crates (`core`, `formula`, `graph`, `store`, `import`,
  `ui`, `app`, `cli`), fixtures, xtask. Crates are published to crates.io individually from the
  workspace once they reach 0.1, with the workspace version lockstepped (`version.workspace =
  true`), like egui does.
- `causl-engine-core`: a public mirror, see [ADR-003](adr-003-causl-dependency.md).

The full crate layering and the reason for each boundary are in
[topology](../overview/topology.md).

# Alternatives

**One repo per crate.** Independent versioning and smaller clones. Lost: at specification stage
every crate changes with every other; a type change in `sheetbase-formula::Value` touches core,
store, ui and cli in one commit, which eight repos turn into eight PRs and a dependency dance.
The clone size argument is void until there are large binaries, and fixtures are 25 MB total.

**One repo including the spec.** Simplest. Lost because the spec is reviewed by people who will
never run cargo, OKF wants a bundle to be shippable as a directory, and the spec's history (ADR
changes) should not be interleaved with code commits.

**Two repos, no mirror (depend on Gitea directly).** Lost: contributors without a Gitea account
cannot build. See ADR-003.

# Consequences

- `cargo xtask layers` enforces the layer table so the single workspace does not rot into a
  ball.
- When the server arrives (post v1), it is a ninth crate in the same workspace, not a repo.
