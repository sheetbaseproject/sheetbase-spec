---
type: Decision
title: "ADR-001: Apache-2.0 for the whole org"
description: Every sheetbase repo is Apache-2.0 only, not MIT OR Apache-2.0, because Grist-derived material cannot be offered under MIT and a single licence keeps NOTICE handling simple.
tags: [decision, licence]
status: draft
decision_id: ADR-001
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-licence
    resource: https://github.com/gristlabs/grist-core/blob/main/LICENSE
    title: grist-core LICENSE (Apache-2.0)
  - id: gridcraft-licence
    resource: https://github.com/storytold/gridcraft
    title: gridcraft, workspace license = "MIT OR Apache-2.0", LICENSE-MIT, LICENSE-APACHE, NOTICE
  - id: causl-licence
    resource: /Users/rom/workspace/causl/causl-core-rs/LICENSE
    title: causl-core-rs LICENSE (MIT, Copyright (c) 2026 Roman Goldmann)
---

# Context

Three upstreams feed sheetbase, with three licences:

- grist-core is Apache-2.0.[^grist-licence] We copy no source, but we do copy the 118 fixture
  documents for golden tests, the metadata schema, and the exact semantics of a few algorithms
  (relabeling, lookup relations). Fixtures are copyrighted works; they travel with the Apache
  notice.
- gridcraft is `MIT OR Apache-2.0`,[^gridcraft-licence] with `NOTICE` carrying "Copyright (c) 2026
  ArtCraft Team and the GridCraft contributors". We copy about 20k lines verbatim (see
  [ADR-012](adr-012-gridcraft-harvest.md)).
- causl-core-rs is MIT.[^causl-licence] We depend on it as a crate and mirror it; we do not copy
  it into our tree.

The Rust ecosystem default is `MIT OR Apache-2.0`. Grist's choice is Apache-2.0.

# Decision

Apache-2.0, alone, for `sheetbase-spec` and `sheetbase`. The Causl mirror stays MIT because it is
upstream's code, not ours.

Compliance mechanics:

- `sheetbase/LICENSE` is the Apache-2.0 text. `sheetbase/NOTICE` carries the project line and
  one entry per harvested origin: the gridcraft project line reproduced from their NOTICE, the
  Adobe and Unicode notices from `crates/pdf` if that crate is ever harvested (it is not in v1),
  and the grist-core line for the fixtures.
- Every file copied from gridcraft keeps a header comment: origin path, commit, "Copyright (c)
  2026 ArtCraft Team and the GridCraft contributors, used under the Apache License 2.0", and a
  one-line statement of modifications as Apache section 4(b) requires.
- No gridcraft trademark material is copied (`docs/brand/`, app icon, identifiers).
- `third_party/` holds a `HARVEST.md` listing every copied file with its origin commit so the
  attribution is auditable.

# Alternatives

**MIT OR Apache-2.0 (Rust default).** Argued by the Rust engineer: fewer questions from
downstream crate users, matches egui and most dependencies. Lost because the dual licence is a
promise that every line can be taken under MIT alone, and the Grist fixtures and any
Grist-derived algorithm text cannot. We would end up with "MIT OR Apache-2.0 except
`fixtures/` and `NOTICE`", which is worse than one licence. Apache-2.0 also carries the explicit
patent grant, which the security role wanted for a project with 3,400 forks' worth of upstream
contributors behind one of its inputs.

**AGPL-3.0 (copyleft, protect against SaaS forks).** Raised and dropped in a minute: it would
make the gridcraft and Causl harvests one-way, stop Grist from ever taking anything back, and
the agentic role noted it deters the embedding use case the CLI exists for.

**Private repos until v1.** Rejected: nothing in any upstream licence requires it, and the
point of putting the spec in a public org is review.

# Consequences

- Contributions are inbound under Apache-2.0 by the repo licence; no CLA for v1. Revisit if a
  company wants to contribute.
- gridcraft has no CLA either and 240k lines from a handful of accounts in one month; the panel
  accepts the harvested files on their stated licence and records the risk here so it is a known
  one.

[^grist-licence]: grist-core LICENSE (Apache-2.0)
[^gridcraft-licence]: gridcraft, workspace license = "MIT OR Apache-2.0", LICENSE-MIT, LICENSE-APACHE, NOTICE
[^causl-licence]: causl-core-rs LICENSE (MIT, Copyright (c) 2026 Roman Goldmann)
