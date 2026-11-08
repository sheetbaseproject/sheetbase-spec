---
type: Overview
title: Product
description: sheetbase is a desktop relational spreadsheet in Rust and egui that reads and writes Grist documents and recalculates through the Causl dependency graph.
tags: [overview, product]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: grist-core
    resource: https://github.com/gristlabs/grist-core
    title: grist-core (Apache-2.0), read at HEAD on 2026-11-07, schema version 47
    author: team:gristlabs
    last_modified: 2026-11-07T06:04:56Z
---

# The product in one paragraph

sheetbase is a relational spreadsheet. A document holds tables; a table holds typed columns;
rows are records with stable integer ids. A column is either data the user typed or a formula
over the record it belongs to (`$Amount * 2`), over references it holds (`$Customer.Name`) or over
other tables (`Orders.lookupRecords(Customer=$id)`). Reference and reference-list columns link
tables. Summary tables group a source table and derive aggregates. A page shows one or more
widgets (grid, card, card list, chart) over tables, and widgets can be linked so selecting a row
in one filters another. Access rules say who may read or change what. Every change is an action
that can be undone.

That is Grist's model,[^grist-core] and we keep it on purpose: it is proven, it has a file
format with a decade of documents behind it, and the help pages that explain it already exist.
What changes is the implementation: Rust instead of TypeScript and Python, egui instead of a
browser, Causl instead of Grist's hand-rolled dependency engine, and a formula language that is
a Python-expression subset instead of a Python sandbox.

# Who it is for

- People who open a `.grist` file and want a native desktop app for it: fast, offline, one
  binary.
- Developers who want a headless document engine they can script (`sb apply`, `sb export`) or
  drive from an agent through a local JSON-RPC surface, without a Node server and a Python
  sandbox in the loop.
- Us, as the first real consumer of Causl in Rust beyond the wasm bridge.

# Not this

Not a web app, not a collaboration server, not an Excel clone. Those are listed with reasons in
[Out of scope for v1](out-of-scope.md). It is also not a fork of Grist: no Grist source is
copied, only the data model, the metadata schema and the fixture documents used as golden tests.

# The shape of the system

```
 .grist / .sheetbase (SQLite)
          |
   sheetbase-store  ----->  sheetbase-core  <-----  sheetbase-formula
   (rows, schema,           (Document, actions,     (parse, compile,
    action history)          engine, relations,      evaluate, functions)
                             view model)
                                  |
                           sheetbase-graph
                           (Causl behind a facade:
                            column-level nodes,
                            one commit per bundle)
                                  |
          +-----------------------+-----------------------+
   sheetbase-ui (egui)      sheetbase-cli (headless)   sheetbase-import
   grid, cards, charts,     sb apply/export/check      .grist .xlsx .csv
   editors, pages
          |
   sheetbase-app (eframe desktop binary)
```

The dependency graph is the spine. A user action becomes doc actions, doc actions write the
data columns they touch, and one Causl commit settles every formula column, lookup index, summary
table and view-model node that depends on them, glitch-free, before the UI draws the next
frame. The arithmetic that makes this fit in memory and in a frame budget is in
[Causl mapping](../model/causl-mapping.md).

[^grist-core]: grist-core (Apache-2.0), read at HEAD on 2026-11-07, schema version 47
