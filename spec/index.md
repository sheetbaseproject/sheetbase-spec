---
okf_version: "0.2"
---

# Subdirectories

* [cli](cli/index.md) - The desktop binary's command line and the headless tool sb.
* [components](components/index.md) - One concept per crate (and one for the spec repo): purpose, public API surface, dependencies, size estimate, and which requirements it carries.
* [decisions](decisions/index.md) - Every contested design decision as an ADR, with the alternatives that lost, why they lost, and who on the panel dissented.
* [formula](formula/index.md) - SFL, the sheetbase formula language: grammar and semantics, the function library, the sandbox, and migration of Grist Python formulas.
* [model](model/index.md) - The document model, its storage, the action pipeline, and how all of it maps onto Causl commits, with Rust signatures and SQL.
* [overview](overview/index.md) - What sheetbase is, what v1 covers, what it leaves out, and the words the rest of the spec uses.
* [plan](plan/index.md) - Milestones M0 to M8 with exit criteria, and the open questions with recommended defaults.
* [quality](quality/index.md) - Testing strategy, performance budgets with benchmark gates, the security model and the error catalogue.
* [references](references/index.md) - The large tables that do not fit a design concept: the xldatagrid traceability table, the gridcraft harvest list, the Grist source map and the licence inventory.
* [requirements](requirements/index.md) - Testable requirements with ids, priorities (must / should / could) and a verification method each; grouped by area in one concept per area.
* [ui](ui/index.md) - The egui front end: architecture, the grid widget, keyboard model, selection state machine, cell types and editors, the full widget catalogue, accessibility, theming with measured contrast, and the 60 fps performance plan.
