---
type: Component
title: sheetbase-import
description: L2 crate for opening foreign documents (.grist with formula classification), importing csv/tsv/xlsx through an ImportPlan, and exporting csv/tsv/xlsx.
tags: [component, crate, import, export]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Public surface

```rust
pub fn sniff(bytes: &[u8], name: &str) -> Format;                    // Grist | Sheetbase | Csv | Tsv | Xlsx | Unknown
pub fn open_grist(path: &Path) -> Result<(Store, Document, FormulaReport), ImportError>;   // wraps Store::open + classification
pub struct ImportPlan { pub source: SourceDesc, pub target: Target /* NewTable{name} | Existing{table, mapping} */, pub columns: Vec<ColumnPlan /* name, guessed type, sample, mapped_to */>, pub key: Option<KeyStrategy>, pub row_count: usize }
pub fn plan_csv(bytes: &[u8], opts: &CsvOptions, doc: &Document) -> Result<ImportPlan, ImportError>;
pub fn plan_xlsx(bytes: &[u8], sheet: Option<&str>, doc: &Document) -> Result<ImportPlan, ImportError>;
pub fn execute(plan: &ImportPlan, source: &[u8], engine: &mut Engine, user: &User) -> Result<ActionBundle, ImportError>;   // AddTable + BulkAddRecord in chunks chained by linkId
pub mod export {
    pub fn csv(engine: &Engine, section: SectionRef, opts: &DsvOptions, out: &mut dyn Write) -> Result<(), ImportError>;
    pub fn xlsx(engine: &Engine, scope: ExportScope, out: &mut dyn Write) -> Result<(), ImportError>;
}
```

Type guessing follows Grist's `guessColInfo` order; dates use the harvested `parse.rs` shapes plus
ISO; `.xlsx` cells typed from calamine's `Data` enum; formulas in xlsx are imported as values
(the cached result) with a report line.

# Dependencies

`calamine 0.38`, `rust_xlsxwriter 0.102`, `csv 1`, `encoding_rs`, `sheetbase-core`,
`sheetbase-store`, `sheetbase-formula`.

# Size

About 4k lines.

# Requirements carried

REQ-IO-01 to 04.
