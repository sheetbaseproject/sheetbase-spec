# Component Design

* [Access rules](access-rules.md) - Grist's ACL model implemented in the engine: resources, rules, the permissions grammar, the predicate grammar and its parsed form, user attributes, the default rule set, the SPECIAL table, and where each check runs.
* [Actions and undo](actions-and-undo.md) - The action pipeline: user actions (all 43 Grist ones minus the import transforms), their expansion into doc actions, inverse computation, bundles, and how one bundle becomes one Causl commit.
* [Causl mapping](causl-mapping.md) - Exactly how the document becomes a Causl graph: the three namespaces, every node kind with its id pattern and value, the sheetbase-graph facade trait, the commit protocol, subscriptions, and what happens on each RaceClass.
* [Document model](document-model.md) - The in-memory document: tables, typed columns, the columnar row store, stable ids, and the metadata tables as typed records, with the Rust types sheetbase-core exposes.
* [Lookups and summary tables](lookups-and-summary.md) - lookupRecords/lookupOne/CONTAINS/order_by as index nodes and relations; reference and reference-list columns with two-way references; summary tables as auto-maintained tables with a helper node, group column, auto-created rows and auto-removed empty groups.
* [Relations and recalc](relations-and-recalc.md) - The formula-column compute in detail: dirty sets and the DeltaLog, relation types and affected-row mapping, the staging overlay and rollback, trigger formulas, the cycle-group evaluator, and error cells.
* [Storage (SQLite)](storage-sqlite.md) - The on-disk layout: Grist's user tables and _grist_* metadata at schema version 47, the _gristsys_* system tables we read, and the _sheetbase_* tables we add; transactions, migrations, the load and save paths.
* [Value encoding](value-encoding.md) - How a Value crosses the three boundaries: the Grist wire format (JSON with object codes), SQLite storage (affinities, JSON lists, marshal blobs) and the formula interpreter (rich objects).
* [View model](view-model.md) - Pages, views, sections, fields, sort and filter specs, linking, widget options, card layouts and conditional formatting, all derived as Causl view: nodes from model: data and controller: inputs.

# Overview

* [About the model section](_about.md) - The document model, its storage, the action pipeline, and how all of it maps onto Causl commits, with Rust signatures and SQL.
