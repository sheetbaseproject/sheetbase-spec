---
type: Component Design
title: Causl mapping
description: "Exactly how the document becomes a Causl graph: the three namespaces, every node kind with its id pattern and value, the sheetbase-graph facade trait, the commit protocol, subscriptions, and what happens on each RaceClass."
tags: [model, causl, graph]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: causl-compute
    resource: /Users/rom/workspace/causl/causl-core-rs/tools/engine-rs-core/src/compute_callback.rs
    title: ComputeCallback trait (dep_values slice, returned read set replaces deps)
  - id: causl-phase
    resource: /Users/rom/workspace/causl/causl-core-rs/tools/engine-rs-core/src/phase_step.rs
    title: transition_phased_in_place_with_callbacks, PhaseStep::RecomputeAffected
  - id: causl-race
    resource: /Users/rom/workspace/causl/causl-core-rs/tools/engine-rs-core/src/race_class.rs
    title: RaceClass variants
---

# Namespaces

String ids are the facade's; Causl sees dense `NodeId`s. Three prefixes, enforced by the
registry at creation and by a debug assertion on every dependency edge:

| Namespace | Who writes it | Who may depend on it | Lifetime |
|---|---|---|---|
| `model:` | the action pipeline (inputs) and computes (deriveds) | `model:`, `view:` | the document |
| `controller:` | the UI or CLI, outside the action pipeline (cursor, scroll, selection, open menu, filter drafts) | `view:` only | the session |
| `view:` | computes only | `view:` | the session |

A `model:` node may never read a `controller:` or `view:` node; the tracked reader refuses the
read with `GraphError::NamespaceViolation { from, to }`, which fails the commit. This is what
keeps the document's data independent of what is on screen.

# Node catalogue

| Id pattern | Kind | Value | Written by |
|---|---|---|---|
| `model:#now` | input | `{"v": n}` | `UpdateCurrentTime` |
| `model:{T}.#schema` | input | `{"v": n}` | any schema action on `T` (replaces Grist's `Node(table, None)`) |
| `model:{T}.#rows` | input | `{"v": n}` | add/remove rows (dirty set = the ids) |
| `model:{T}.{C}` (data column) | input | `{"v": n}` | `BulkUpdateRecord`/`BulkAddRecord` touching `C`; trigger formulas write here too |
| `model:{T}.{C}` (formula column) | derived | `{"v": n}` | its compute |
| `model:{T}.#lookup#{cols}` | derived | `{"v": n}` | lookup index compute over the key columns |
| `model:{T}.#lookup#{cols}#{sort}` | derived | `{"v": n}` | sorted lookup index |
| `model:{T}.#summary#{S}` | derived | `{"v": n}` | summary helper compute (source row to group row) |
| `model:{T}.#cycle#{n}` | derived | `{"v": n}` | cycle group compute ([ADR-006](../decisions/adr-006-cycle-groups.md)); member columns are inputs it writes |
| `model:acl` | input | `{"v": n}` | changes to `_grist_ACLRules`/`_grist_ACLResources` |
| `controller:section:{id}:cursor` | input | `{"row": id, "col": colRef, "edit": seq}` | UI cursor moves |
| `controller:section:{id}:selection` | input | selection state JSON | UI |
| `controller:section:{id}:filterdraft` | input | unsaved filter JSON | UI |
| `controller:page` | input | `{"view": id}` | UI |
| `controller:user` | input | the `User` as JSON | process start, `--as-user` |
| `view:section:{id}:linkfilter` | derived | `{"filters": {...}, "operations": {...}}` | compute from source section cursor/selection and `model:` columns |
| `view:section:{id}:rows` | derived | `{"v": n}` (row list in the view store) | sort + filter + link filter + ACL row pruning over `model:{T}.#rows` and sort/filter columns |
| `view:section:{id}:cells` | derived | `{"v": n}` | ACL cell censoring map for the visible rows |
| `view:section:{id}:styles` | derived | `{"v": n}` | conditional-format resolution per visible row |
| `view:page:{id}:layout` | derived | layout JSON | from `_grist_Views.layoutSpec` and section list |

Node count for a large document: about 1000 column nodes + 300 index/helper + 5 per section x
400 sections = about 3300 nodes.

# The facade

```rust
// sheetbase-graph
pub trait Graph {
    type Reader<'a>: TrackedReader where Self: 'a;

    fn create_input(&mut self, id: &str, initial: Token) -> Result<NodeRef, GraphError>;
    fn create_derived(&mut self, id: &str, compute: Box<dyn Compute>) -> Result<NodeRef, GraphError>;
    fn dispose(&mut self, node: NodeRef) -> Result<(), GraphError>;
    fn lookup(&self, id: &str) -> Option<NodeRef>;
    fn id_of(&self, node: NodeRef) -> &str;

    /// One atomic commit. `writes` bump input tokens. Every affected derived recomputes once,
    /// topologically, glitch-free. Returns which nodes changed and the new graph time.
    fn commit(&mut self, intent: &str, writes: &[(NodeRef, Token)], host: &mut dyn ComputeHost)
        -> Result<CommitOutcome, GraphError>;

    fn version(&self, node: NodeRef) -> u64;          // Causl: State::node_version; Reference: own counter
    fn time(&self) -> u64;                            // GraphTime
    fn subscribe(&mut self, node: NodeRef, sub: SubscriberId) -> Result<(), GraphError>;
    fn unsubscribe(&mut self, sub: SubscriberId);
    fn dependencies(&self, node: NodeRef) -> Vec<NodeRef>;
    fn dependents(&self, node: NodeRef) -> Vec<NodeRef>;
}

#[derive(Copy, Clone, Eq, PartialEq, Hash, Debug)] pub struct NodeRef(u32);      // dense; wraps causl NodeId slot+gen in CauslGraph
#[derive(Clone, PartialEq, Debug)] pub struct Token(pub u64);                     // {"v": n} in Causl

pub trait Compute: Send {
    /// Runs inside a commit. May read any node through `reader` (tracked); must write only
    /// through `host.staging()`; must be deterministic; must not panic (errors are returned).
    fn run(&mut self, reader: &mut dyn TrackedReader, host: &mut dyn ComputeHost) -> Result<Token, ComputeFailure>;
}

pub trait TrackedReader {
    fn read(&mut self, node: NodeRef) -> Result<Token, GraphError>;      // records the dependency
    fn version_seen(&self, node: NodeRef) -> Option<u64>;                // what this derived saw last time
    fn self_node(&self) -> NodeRef;
}

pub trait ComputeHost {
    fn store(&self) -> &ColumnStoreView;                                 // read-only data access (with staging applied)
    fn staging(&mut self) -> &mut CommitStaging;                         // writes
    fn deltas(&self, node: NodeRef, since_version: u64) -> RowSet;       // dirty rows of a column node since a version
    fn formulas(&self) -> &FormulaRegistry;
    fn now(&self) -> f64;
}

pub struct CommitOutcome { pub time: u64, pub changed: Vec<NodeRef>, pub intent: SmolStr }

#[derive(thiserror::Error, Debug)]
pub enum GraphError {
    #[error("cycle through {path:?}")]                 Cycle { path: Vec<SmolStr> },          // retryable: false (core retries once after regrouping)
    #[error("compute {node} failed: {reason}")]        ComputeFailed { node: SmolStr, reason: SmolStr }, // retryable: false
    #[error("{from} may not depend on {to}")]          NamespaceViolation { from: SmolStr, to: SmolStr }, // retryable: false, programming error
    #[error("unknown node {id}")]                      UnknownNode { id: SmolStr },
    #[error("node {id} already exists")]               Duplicate { id: SmolStr },
    #[error("commit already in progress")]             Reentrant,                              // retryable: true (after the current commit)
    #[error("node {id} was disposed")]                 Disposed { id: SmolStr },
    #[error("backend: {0}")]                           Backend(SmolStr),                       // Causl RaceClass not covered above
}
```

Wrapper test from the user's Rust rules: `NodeRef` and `Token` are conversions (dense id to
string-keyed registry; `u64` to `JsonValue`), `Graph` is a contract implemented twice,
`TrackedReader` enforces the namespace invariant. Nothing here forwards one call to one call.

# CauslGraph implementation notes

- `commit` builds `Action::CommitWithValues { intent, writes: Vec<(NodeId, JsonValue::Object{"v"})> }`
  and calls `transition_phased_in_place_with_callbacks(&mut state, &action, DEFAULT_ENGINE_ID,
  &callback, &subscriber, &mut steps)`.[^causl-phase] The `ComputeCallback` impl looks up the
  `Box<dyn Compute>` for `derived_id`, wraps `&mut State` in a `TrackedReader` that reads
  `state.get_value(dep)` and records the `NodeId`, runs it, and returns `(JsonValue token,
  SmallVec of read NodeIds)`.[^causl-compute] Because Causl replaces the derived's deps with
  the returned set, dynamic dependencies and stale-edge dropping come for free.
- `dep_values` from Causl are ignored (we read through `state`), which is allowed ("the callback
  may read `state`").
- `commit_history_cap = 0`, `commit_log_cap = Some(64)` (the UI's history strip uses the commit
  log's intents), retention off.
- `State.committing` is set by the facade around the transition so `Reentrant` is detected.
- `RaceClass` mapping:[^causl-race] `CycleClosed { path }` to `GraphError::Cycle`,
  `ComputeThrew` to `ComputeFailed`, `CommitInProgress` to `Reentrant`, `NodeDisposed`/`UnknownNode`
  /`SlotOutOfRange` to the named variants, everything else (`GlitchPropagation`,
  `ReplayDivergence`, `StructurallyInvalid`, ...) to `Backend` and logged at error level since
  they indicate an engine bug.
- `steps` (`PhaseStep::RecomputeAffected`) are kept for `sb explain`, which prints the recompute
  order of the last commit.

# ReferenceGraph

A `Vec<Node>` with `deps`, `dependents`, `version`, an explicit Kahn drain over the affected set
seeded from `writes`, the same `TrackedReader`/`ComputeHost` contracts, and a `CommitStaging`
discarded on any error. About 600 lines. It is the oracle in differential proptests
([testing](../quality/testing.md)) and the build for `--no-default-features`.

# Subscriptions and the UI

The UI subscribes to `view:*` nodes it draws. After `commit`, `CommitOutcome.changed` plus the
subscriber firings tell the frame loop what to repaint; `node version` is the memo key for
cached galleys and row lists (never value identity, per Causl guidance).

[^causl-compute]: ComputeCallback trait (dep_values slice, returned read set replaces deps)
[^causl-phase]: transition_phased_in_place_with_callbacks, PhaseStep::RecomputeAffected
[^causl-race]: RaceClass variants
