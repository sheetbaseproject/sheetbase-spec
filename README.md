# sheetbase-spec

This is the specification for sheetbase, a Rust + egui relational spreadsheet in the spirit of
Grist: documents hold typed tables, formula columns are written over records and references,
summary tables and linked views derive from the data, access rules gate what a user sees, and
SQLite is the store. Underneath, the Causl dependency graph drives recalculation and the view
model.

Status: specification stage. No code yet, on purpose... the point of this repo is to settle the
design before the first crate lands.

## Layout

- `spec/` is the specification as an OKF v0.2 knowledge bundle: markdown files with YAML
  frontmatter, `index.md` listings for progressive disclosure, `log.md` for history. Start at
  `spec/index.md`.
- `spec/decisions/` holds every contested decision as an ADR, each with the alternatives that lost
  and why.
- `spec/references/` holds the big tables: the xldatagrid traceability table, the gridcraft
  harvest list, the Grist source map.
- `tools/okf_check.py` validates the bundle. It needs only the Python standard library plus
  PyYAML, and runs under `python3 -I`.

## Validate

```
python3 -I tools/okf_check.py spec
```

## Related repos

- https://github.com/sheetbaseproject/sheetbase (the cargo workspace, specification stage)
- https://github.com/sheetbaseproject/causl-engine-core (public mirror of the Causl engine crate)

## Licence

Apache-2.0, see `LICENSE`.
