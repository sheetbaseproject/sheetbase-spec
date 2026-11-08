---
type: Component Design
title: Security model
description: "Trust boundaries of a desktop document app: untrusted files, untrusted formulas, the clipboard, imports, the headless surface; what each boundary enforces and how it is tested."
tags: [quality, security]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
---

# Boundaries

| Boundary | Untrusted input | Enforcement |
|---|---|---|
| Document file | SQLite bytes, metadata JSON, formulas, marshal blobs, attachments | `rusqlite` bundled SQLite with `SQLITE_DBCONFIG_DEFENSIVE` on; `PRAGMA quick_check` on open; every JSON field parsed with size caps (1 MiB per metadata cell) and unknown keys preserved not interpreted; marshal depth 64 / 16 MiB; attachments are bytes shown through `image` with decode limits (64 Mpx) and never executed or opened by us (the OS opener is a user action with a confirmation) |
| Formulas | SFL source | the [sandbox](../formula/sandbox.md): no host access by construction, fuel, depth, size caps, no panics (catch_unwind as the last line) |
| Access rules | predicate text, user attribute table names | parsed by our grammar, evaluated without I/O; a malformed rule denies (`BadRule`) rather than allows |
| Clipboard | HTML and text from any app | HTML parsed with a bounded parser (`html5ever` is too heavy; a 300-line table-only parser with size cap 300 MB); `data-grist-raw-value` JSON decoded with the same caps as the file; no script, no external resources |
| Imports | csv, xlsx | csv with size cap 512 MiB and row cap 10M; calamine with its own limits; zip bombs bounded by calamine's streaming (we cap uncompressed sheet size at 1 GiB) |
| `sb serve` | JSON-RPC from a local process | stdio only, never a socket; params validated by serde into typed enums; actions pass through the same ACL as the GUI; `--read-only` refuses `doc.apply` |
| Paths | file dialog and CLI paths | no path is ever derived from document content (attachments are blobs, not paths); `SELF_HYPERLINK` builds URLs from settings, not from the file |
| Network | none | no crate in the workspace opens a socket; `cargo deny` bans the HTTP and TLS crates; the About dialog states it |

# Process

- `#![forbid(unsafe_code)]` in every crate except `sheetbase-app` (platform glue) where it is
  `deny` with per-item `allow` and a comment.
- `cargo deny` runs in CI: licences (allow Apache-2.0, MIT, BSD-2/3, ISC, Unicode-3.0, Zlib,
  MPL-2.0 for one known crate if needed, OFL-1.1 for fonts), bans (network crates in library
  crates, `openssl`), advisories.
- Fuzz targets listed in [testing](testing.md) run nightly; a crash is a P1 issue.
- No telemetry by default; the opt-in migration counter sends only construct counts.
- Release binaries are built reproducibly (`cargo build --locked`, `SOURCE_DATE_EPOCH`) and
  signed on macOS and Windows; checksums published with each release.

# Not defended

Side channels, a malicious OS, a malicious egui dependency (we pin and review bumps). A user
who opens an attachment externally trusts their OS opener. Documents are not encrypted at rest
(SQLite file); that is a feature request, not a v1 goal.
