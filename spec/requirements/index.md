# Overview

* [About the requirements](_about.md) - Testable requirements with ids, priorities (must / should / could) and a verification method each; grouped by area in one concept per area.

# Requirement

* [Requirements: access rules and views](req-acl-and-views.md) - REQ-ACL and REQ-VIEW: rule grammar and enforcement for an explicit user, and the view model (pages, sections, fields, sort, filter, linking, styles).
* [Requirements: actions, engine and graph](req-actions-and-engine.md) - REQ-ACTION, REQ-ENGINE and REQ-GRAPH: user actions, inverses, atomic bundles, glitch-free recalculation through Causl, relations, lookups, summaries, cycles, trigger formulas, the facade.
* [Requirements: formula language](req-formula.md) - REQ-FORMULA: SFL compatibility with Grist formulas, the function library, the sandbox limits, migration classification and conversion.
* [Requirements: import/export, CLI, agents, security, app, engine performance](req-io-cli-security.md) - REQ-IO, REQ-CLI, REQ-AGENT, REQ-SEC, REQ-APP and the engine side of REQ-PERF.
* [Requirements: document model and storage](req-model-and-store.md) - REQ-MODEL and REQ-STORE: Grist schema 47 compatibility, columnar store, value encoding, migrations, history.
* [Requirements: UI, accessibility and UI performance](req-ui.md) - REQ-UI, REQ-A11Y and REQ-PERF (UI part): the grid and widget catalogue, keyboard model, selection, clipboard, theming with measured contrast, AccessKit tree, 60 fps budget.
