---
type: Component Design
title: Theming
description: The token set in light and dark, with every key text/background pair's WCAG ratio measured (4.5:1 normal text, 3:1 UI), the contrast test that gates it, and how Grist's per-cell colours and the user's preferences compose.
tags: [ui, theming, contrast, a11y]
status: draft
generated: { by: human:spdrman, at: 2026-11-07T19:30:00Z }
sources:
  - id: gridcraft-theme
    resource: https://github.com/storytold/gridcraft/blob/main/crates/ui-egui/src/theme.rs
    title: gridcraft theme.rs (Tokens struct, contrast(), WCAG test in both themes)
---

# Structure (gridcraft's pattern, our values)[^gridcraft-theme]

```rust
pub struct Theme { pub mode: Mode /* Light | Dark */, pub t: Tokens, pub high_contrast_gridlines: bool }
pub struct Tokens {
    pub bg: Color32, pub text: Color32, pub muted: Color32, pub placeholder: Color32,
    pub gridline: Color32, pub gridline_hc: Color32, pub header_bg: Color32, pub frozen_bg: Color32, pub zebra: Color32,
    pub accent: Color32, pub cursor: Color32, pub focus: Color32, pub range_bg: Color32, pub selected_row_bg: Color32,
    pub link: Color32, pub error: Color32, pub warning: Color32,
    pub badge_bg: Color32, pub badge_text: Color32, pub tooltip_bg: Color32, pub tooltip_text: Color32,
    pub panel_bg: Color32, pub panel_border: Color32, pub menu_bg: Color32, pub menu_hover: Color32, pub menu_text: Color32,
    pub choice_default_bg: Color32, pub choice_default_text: Color32,
}
pub fn contrast(a: Color32, b: Color32) -> f32;   // WCAG 2.x relative luminance ratio
```

`Theme::from_mode(Mode)` returns the built-in set; `egui::Visuals` is derived from the tokens so
built-in widgets match. The system theme is followed by default (`eframe` exposes it; on Linux
the portal via gridcraft's `desktop_theme.rs`).

# Values and measured ratios

Light:

| Pair | Colours | Ratio | Needs | |
|---|---|---|---|---|
| text on bg | `#1F2329` on `#FFFFFF` | 15.78:1 | 4.5 | ok |
| muted on bg | `#5B6573` on `#FFFFFF` | 5.91:1 | 4.5 | ok |
| placeholder on bg | `#6B7684` on `#FFFFFF` | 4.62:1 | 4.5 | ok |
| text on header_bg / frozen_bg | `#1F2329` on `#F3F5F7` | 14.44:1 | 4.5 | ok |
| text on zebra | `#1F2329` on `#F7F9FB` | 14.95:1 | 4.5 | ok |
| text on range_bg | `#1F2329` on `#E6F4EC` | 13.91:1 | 4.5 | ok |
| text on selected_row_bg | `#1F2329` on `#DCEFE4` | 13.16:1 | 4.5 | ok |
| link on bg | `#0B5FA5` on `#FFFFFF` | 6.57:1 | 4.5 | ok |
| error on bg | `#B42318` on `#FFFFFF` | 6.57:1 | 4.5 | ok |
| error on range_bg | `#B42318` on `#E6F4EC` | 5.80:1 | 4.5 | ok |
| warning on bg | `#8A5A00` on `#FFFFFF` | 5.93:1 | 4.5 | ok |
| badge_text on badge_bg | `#FFFFFF` on `#0F7B5F` | 5.23:1 | 4.5 | ok |
| tooltip_text on tooltip_bg | `#FFFFFF` on `#1F2329` | 15.78:1 | 4.5 | ok |
| cursor / accent on bg | `#0F7B5F` on `#FFFFFF` | 5.23:1 | 3.0 | ok |
| cursor on range_bg | `#0F7B5F` on `#E6F4EC` | 4.61:1 | 3.0 | ok |
| cursor on selected_row_bg | `#0F7B5F` on `#DCEFE4` | 4.36:1 | 3.0 | ok |
| focus on header_bg | `#0F7B5F` on `#F3F5F7` | 4.78:1 | 3.0 | ok |
| gridline on bg (decorative) | `#D8DDE3` on `#FFFFFF` | 1.37:1 | exempt (1.4.11 decorative) | note |
| gridline_hc on bg | `#6F7985` on `#FFFFFF` | 4.42:1 | 3.0 | ok |

Dark:

| Pair | Colours | Ratio | Needs | |
|---|---|---|---|---|
| text on bg | `#E6EAF0` on `#1B1F24` | 13.72:1 | 4.5 | ok |
| muted on bg | `#A3ACB8` on `#1B1F24` | 7.22:1 | 4.5 | ok |
| placeholder on bg | `#8F99A6` on `#1B1F24` | 5.74:1 | 4.5 | ok |
| text on header_bg / frozen_bg | `#E6EAF0` on `#23292F` | 12.16:1 | 4.5 | ok |
| text on zebra | `#E6EAF0` on `#1F242A` | 12.94:1 | 4.5 | ok |
| text on range_bg | `#E6EAF0` on `#1E3A2D` | 10.24:1 | 4.5 | ok |
| text on selected_row_bg | `#E6EAF0` on `#24493A` | 8.32:1 | 4.5 | ok |
| link on bg | `#8CC3F2` on `#1B1F24` | 8.83:1 | 4.5 | ok |
| error on bg | `#F28B82` on `#1B1F24` | 6.93:1 | 4.5 | ok |
| error on range_bg | `#F28B82` on `#1E3A2D` | 5.18:1 | 4.5 | ok |
| warning on bg | `#E3B341` on `#1B1F24` | 8.51:1 | 4.5 | ok |
| badge_text on badge_bg | `#0E1A14` on `#5CCB97` | 8.88:1 | 4.5 | ok |
| tooltip_text on tooltip_bg | `#1B1F24` on `#E6EAF0` | 13.72:1 | 4.5 | ok |
| cursor / accent on bg | `#5CCB97` on `#1B1F24` | 8.24:1 | 3.0 | ok |
| cursor on range_bg | `#5CCB97` on `#1E3A2D` | 6.15:1 | 3.0 | ok |
| cursor on selected_row_bg | `#5CCB97` on `#24493A` | 5.00:1 | 3.0 | ok |
| focus on header_bg | `#5CCB97` on `#23292F` | 7.31:1 | 3.0 | ok |
| gridline on bg (decorative) | `#3A424D` on `#1B1F24` | 1.63:1 | exempt | note |
| gridline_hc on bg | `#8A94A0` on `#1B1F24` | 5.38:1 | 3.0 | ok |

Gridlines are decorative separators (the cell boundary is also conveyed by alignment and by the
header), so WCAG 1.4.11 does not require 3:1; the `high_contrast_gridlines` preference switches
to `gridline_hc`, which does meet it, and is the default when the OS reports a high-contrast
preference. The ratios above were computed with the WCAG 2.x formula and are re-computed by
`theme::tests::every_pair_meets_wcag_in_both_themes`, which lists exactly these pairs and fails
the build on regression.

# User colours

Grist lets users set `textColor`/`fillColor` per column, per rule and per choice. We render them
as given (the user's intent wins), and the creator panel shows the computed ratio next to the
picker with an "AA" or "fails AA" badge, computed with the same `contrast()`. Choice colours
without a text colour get `choice_default_text` chosen per fill (black or white, whichever
contrasts more).

# Density and type

Base font 14 pt (UI) and 13 pt (cells), scaled by `Prefs.interface_scale`. Row height 24 pt
compact (Grist default), 32 pt comfortable. Fonts: the system UI font via the harvested font
discovery (`fonts.rs`) with egui's built-in as fallback; monospace for formulas.

[^gridcraft-theme]: gridcraft theme.rs (Tokens struct, contrast(), WCAG test in both themes)
