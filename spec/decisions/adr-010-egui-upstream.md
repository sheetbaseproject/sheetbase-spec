---
type: Decision
title: "ADR-010: egui 0.37 from upstream with eframe and wgpu, no fork"
description: The UI uses released egui/eframe/egui_extras/egui_kittest 0.37 from crates.io with the wgpu backend and AccessKit on; gridcraft's egui fork is not inherited, and its patches are tracked as upstream issues to watch.
tags: [decision, ui, egui]
status: draft
decision_id: ADR-010
decision_status: accepted
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: egui-crates
    resource: https://crates.io/crates/egui
    title: egui 0.37.0, eframe 0.37.0, egui_kittest 0.37.0, egui_extras 0.37.0 (MIT OR Apache-2.0), released 2026-10-15
  - id: gridcraft-cargo
    resource: https://github.com/storytold/gridcraft/blob/main/Cargo.toml
    title: gridcraft Cargo.toml, [patch.crates-io] replacing the egui family with storytold/egui and winit with storytold/winit
---

# Context

egui 0.37.0 shipped 2026-10-15 with eframe, egui_extras and egui_kittest at the same
version.[^egui-crates] gridcraft patches the entire egui family and winit with its own forks for
ordered IME reset, Wayland clipboard through winit, bidi control levels in epaint, and Latin
layout key reporting for shortcuts.[^gridcraft-cargo]

# Decision

- `egui = "0.37"`, `eframe = { version = "0.37", features = ["wgpu", "accesskit", "persistence"] }`,
  `egui_extras = { version = "0.37", default-features = false, features = ["image"] }`,
  `egui_kittest = { version = "0.37", features = ["wgpu", "snapshot"] }` for tests.
- Renderer: wgpu (Metal, Vulkan, DX12), with `glow` as a feature-gated fallback for machines
  where wgpu adapter probing fails (gridcraft's probe logic in `apps/gridcraft/src/graphics.rs`
  is adapted).
- No `[patch.crates-io]` on egui or winit. The four fork patches become tracked upstream issues
  in our `xtask upstream-watch` list; where a patch matters for us (Latin layout key reporting
  for shortcuts on non-Latin keyboards, and IME ordering in the cell editor) we implement a
  workaround in `sheetbase-ui` (shortcut matching on `Key` plus `physical_key` fallback) rather
  than fork.
- Text: egui's built-in text layout with a galley cache in the grid ([performance](../ui/performance.md)).
  System font discovery through gridcraft's `fonts.rs` (skrifa, MIT OR Apache-2.0) adapted.

# Alternatives

**Inherit gridcraft's forks.** Gets their fixes today. Lost: a fork of egui plus winit is a
maintenance debt that compounds with every egui release (they are at 0.37 already, meaning a
rebase per release), and the fixes are candidates for upstream anyway.

**iced, Slint, GPUI, Dioxus native.** The brief says egui; the panel still checked. iced's
retained model fits a grid well but its table virtualisation story is younger; Slint is
GPL/commercial dual; GPUI is tied to Zed's build. egui's immediate mode is a known risk for a
grid (everything is re-laid every frame) and the performance section budgets for it.

# Consequences

- Accessibility rides on AccessKit through eframe's `accesskit` feature; egui_kittest's
  harness queries the same tree, so a11y assertions and UI tests are one thing.
- HiDPI: egui's points model handles it; the grid snaps gridlines to half-points per
  `pixels_per_point` like gridcraft's `Geo` does.

[^egui-crates]: egui 0.37.0, eframe 0.37.0, egui_kittest 0.37.0, egui_extras 0.37.0 (MIT OR Apache-2.0), released 2026-10-15
[^gridcraft-cargo]: gridcraft Cargo.toml, [patch.crates-io] replacing the egui family with storytold/egui and winit with storytold/winit
