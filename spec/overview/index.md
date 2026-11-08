# Overview

* [About this section](_about.md) - What sheetbase is, what v1 covers, what it leaves out, and the words the rest of the spec uses.
* [Out of scope for v1](out-of-scope.md) - Features deliberately not in v1, each with the reason and what would have to be true to bring it in.
* [Product](product.md) - sheetbase is a desktop relational spreadsheet in Rust and egui that reads and writes Grist documents and recalculates through the Causl dependency graph.
* [Scope of v1](scope.md) - The feature set that v1 ships, stated as a checklist against Grist's feature list so nothing is implied.
* [Repo and crate topology](topology.md) - Three repos under sheetbaseproject (spec, cargo workspace, Causl mirror) and eight crates in one workspace, each boundary justified.

# Reference

* [Glossary](glossary.md) - Grist, Causl and sheetbase terms side by side, so the rest of the spec can use them without re-explaining.
