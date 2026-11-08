---
type: Reference
title: Licence inventory
description: Every upstream and dependency licence that matters, the obligation it creates, and where in the repos the obligation is met.
tags: [references, licence]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

| Source | Licence | What we take | Obligation | Where met |
|---|---|---|---|---|
| grist-core (gristlabs) | Apache-2.0 | 118 fixture documents; schema, semantics (not code) | keep notice with fixtures | `sheetbase/fixtures/grist/NOTICE`, `sheetbase/NOTICE` |
| gridcraft (storytold) | MIT OR Apache-2.0 | ~20k lines copied, ~10k adapted | under Apache-2.0: copyright line, NOTICE project line, modification statements, no trademarks | file headers, `sheetbase/NOTICE`, `third_party/HARVEST.md` |
| causl-core-rs (Roman Goldmann) | MIT | depended on via the public mirror | keep LICENSE and copyright in the mirror; mention in NOTICE as a dependency | `causl-engine-core/LICENSE`, `sheetbase/NOTICE` |
| xldatagrid | MIT (README statement; no LICENSE file in the repo) | behaviour (tests as checklists); no source copied | none for behaviour; if any test fixture text is copied, keep the MIT notice | `sheetbase/NOTICE` mention |
| OKF spec (GoogleCloudPlatform) | Apache-2.0 | the format; the validator is our own code following the reference parser's logic | none beyond attribution courtesy | `sheetbase-spec/README.md` |
| egui, eframe, egui_extras, egui_kittest, egui_plot | MIT OR Apache-2.0 | dependency | none (crates.io metadata) | `cargo deny` |
| rusqlite | MIT | dependency, bundled SQLite (public domain) | none | `cargo deny` |
| calamine | MIT | dependency | none | |
| rust_xlsxwriter | MIT OR Apache-2.0 | dependency | none | |
| jiff | Unlicense OR MIT | dependency | none | |
| proptest, insta, criterion, clap, serde, thiserror, smol_str, indexmap, roaring, regex, tracing, rfd, arboard, accesskit, image, pulldown-cmark | MIT and/or Apache-2.0 | dependencies | none | `cargo deny` allowlist |
| Fonts bundled with egui (`epaint_default_fonts`: Ubuntu-Light under Ubuntu Font Licence 1.0, Hack under MIT + Bitstream Vera, NotoEmoji OFL-1.1, emoji-icon-font MIT) | as listed | transitively bundled | reproduce their notices if we ship them | `sheetbase/NOTICE` (copied from the crate's notices at M5) |

`cargo deny` policy: `allow = ["Apache-2.0", "MIT", "BSD-2-Clause", "BSD-3-Clause", "ISC",
"Unicode-3.0", "Unicode-DFS-2016", "Zlib", "Unlicense", "OFL-1.1", "Ubuntu-font-1.0",
"CC0-1.0", "MPL-2.0"]`, `copyleft = "deny"`, unlisted licences fail the build.
