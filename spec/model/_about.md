---
type: Overview
title: About the model section
description: The document model, its storage, the action pipeline, and how all of it maps onto Causl commits, with Rust signatures and SQL.
tags: [model]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Reading order

1. [Document model](document-model.md): `Document`, `Table`, `Column`, `ColumnStore`, ids.
2. [Value encoding](value-encoding.md): Grist wire codes, SQLite affinities, marshal.
3. [Storage](storage-sqlite.md): the SQLite DDL including `_sheetbase_*`.
4. [Actions and undo](actions-and-undo.md): user actions, doc actions, bundles, inverses.
5. [Causl mapping](causl-mapping.md): nodes, namespaces, commits, the facade.
6. [Relations and recalc](relations-and-recalc.md): the compute, staging, dirty sets, cycle groups.
7. [Lookups and summary tables](lookups-and-summary.md).
8. [Access rules](access-rules.md).
9. [View model](view-model.md): pages, sections, fields, linking, as Causl `view:` nodes.
