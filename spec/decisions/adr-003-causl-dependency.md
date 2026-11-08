---
type: Decision
title: "ADR-003: Causl behind a facade, from a public mirror, with a reference backend"
description: sheetbase-graph exposes a Graph trait; the default backend is causl-engine-core pulled by tag from a public MIT mirror, and a plain ReferenceGraph backend exists for differential tests and for builds without the mirror.
tags: [decision, causl, graph]
status: draft
decision_id: ADR-003
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: causl-cargo
    resource: /Users/rom/workspace/causl/causl-core-rs/tools/engine-rs-core/Cargo.toml
    title: causl-engine-core Cargo.toml (name, version 0.0.0, license MIT, publish = false)
  - id: causl-readme
    resource: /Users/rom/workspace/causl/causl-core-rs/README.md
    title: causl-core-rs README ("Pre-1.0 status", "Development access", GitHub is a downstream mirror)
---

# Context

`causl-engine-core` is `no_std`, `forbid(unsafe_code)`, MIT, `version = "0.0.0"`, `publish =
false`, and lives in a private Gitea repo (`git.opsite.ca/causl/causl-core-rs`, workspace root
`tools/Cargo.toml`).[^causl-cargo] The README says GitHub is a downstream mirror and access is by
account.[^causl-readme] The brief fixes it as THE dependency for all pub-sub dependency
management. An open-source org cannot have a build that needs a private account.

The crate's public surface that we use: `State`, `NodeId { slot, gen }`, `JsonValue`,
`Action::CommitWithValues { intent, writes: Vec<(NodeId, JsonValue)> }`,
`transition_phased_in_place_with_callbacks`, `ComputeCallback::compute(&self, &mut State, NodeId,
&[(NodeId, &JsonValue)]) -> Result<(JsonValue, SmallVec<[NodeId; 4]>), ComputeError>`,
`SubscriberCallback::fire_batch`, `CommitRecord { time, intent, changed_nodes }`, `RaceClass`,
`State::node_version(id)` (release branch), `create_input`, `create_derived`, `register_dep`,
`dispose_node`, `read_at`.

# Decision

1. **Public mirror.** `sheetbaseproject/causl-engine-core` mirrors only the `tools/engine-rs-core`
   crate from the upstream *release* branch (the one with `State::node_version`, `link_writable`,
   the 0.8.0 CHANGELOG). The maintainer syncs it by `git subtree split` and tags
   `v<upstream-version>+sheetbase.<n>`. MIT permits this; the LICENSE and the upstream copyright
   line travel with it. `sheetbase-graph` depends on it as
   `causl-engine-core = { git = "https://github.com/sheetbaseproject/causl-engine-core", tag = "v0.8.1+sheetbase.1", default-features = false, features = ["std"] }`.
   `snapshot` and `enumerator` features are off: we persist our own data, and `State::hash` is
   only used in tests (feature `graph-hash`).
2. **Facade trait.** `sheetbase-graph::Graph` (signatures in
   [sheetbase-graph](../components/sheetbase-graph.md)) is what `sheetbase-core` talks to. It
   is narrower than Causl: string ids, three namespaces, one `commit`, tracked reads inside
   computes, subscriptions, `node_version`. Nothing from `causl_engine_core` is re-exported.
3. **Two backends.** `CauslGraph` (feature `causl`, default) and `ReferenceGraph` (always built):
   a `petgraph`-free, 600-line topological recompute with the same observable contract. The
   reference backend is the oracle for differential proptests and the build for anyone who sets
   `--no-default-features`. It is not a product backend: it is O(graph) per commit, and the
   docs say so.

# Alternatives

**Vendor the crate into `sheetbase/vendor/`.** Simplest build. Lost: 26k lines of someone
else's code in our tree drift silently from upstream, every upstream fix is a manual copy, and
`git blame` becomes useless for it. The mirror keeps upstream history and lets a tag say exactly
which upstream commit we run.

**Depend on Gitea directly, document "ask for access".** Lost on the first principle: an
open-source project that cannot be built from public sources is not open source in practice.

**Publish a fork to crates.io as `sheetbase-causl`.** Lost for now: upstream is `0.0.0` and
`publish = false` by the author's choice; publishing under another name forks the project in the
eyes of the ecosystem. If upstream publishes, the mirror becomes unnecessary and the git
dependency turns into a version. The facade makes that a one-line change.

**No facade, use Causl types everywhere.** The Rust engineer argued facades are pass-through
wrappers. The panel held that the facade meets the *contract* test: Causl speaks dense `NodeId`
and `JsonValue` and has no string ids, no namespaces, no tracked reads (the compute returns its
read set by value), no persistence; the facade supplies all four and is implemented twice.
That is a conversion layer, not a wrapper.

# Consequences

- The sync is a maintainer duty with a checklist in `causl-engine-core/README.md`; the spec's
  M0 milestone starts with it.
- The facade's contract is tested against both backends in the same proptest suite
  ([testing](../quality/testing.md)); divergence fails CI.
- Dissent (performance role): a facade over a `no_std` engine must not add allocations on the
  hot path. Resolved by requiring the facade's `commit` to map string ids to `NodeId` once at
  node creation, never per commit, and by a benchmark gate on facade overhead (under 5 percent
  of engine time on the `recalc_chain_1024` bench).

[^causl-cargo]: causl-engine-core Cargo.toml (name, version 0.0.0, license MIT, publish = false)
[^causl-readme]: causl-core-rs README ("Pre-1.0 status", "Development access", GitHub is a downstream mirror)
