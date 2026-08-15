# OceanPulse — Style Reference
> Deep-sea instrument panel with a bioluminescent signal line.

**Theme:** dark

OceanPulse operates in a deep-ocean control-room mode: a near-black navy canvas, cool light-gray type, and a single bioluminescent cyan accent that marks live signals and rising risk. Data and headings are set in a clean geometric sans at a wide range of sizes — this is a data-density-first system, not an editorial one, so the type never competes with the map or the charts for attention. The rest of the UI is deliberately quiet: thin hairline borders, rounded cards, compact body text, and almost no elevation shadow — depth comes from the surface color steps, the way it would on an actual research-vessel console. A single cyan-to-white gradient (the index trend line, live-data pulses) injects energy into an otherwise monochrome system, evoking sonar and bioluminescence rather than a stock-market ticker.

## Tokens — Colors

| Name | Value | Token | Role |
|------|-------|-------|------|
| Abyss | `#05080c` | `--color-abyss` | Page canvas, footer background, deepest surface — near-black with a cold blue undertone |
| Trench | `#080d14` | `--color-trench` | Card surface, secondary backdrop — one step deeper than the page for visual weight |
| Deep Water | `#101821` | `--color-deep-water` | Elevated panels, subtle UI fills — the first clearly lighter step in the surface stack |
| Reef Shadow | `#1a2530` | `--color-reef-shadow` | Borders, dividers, icon containers, control outlines — the hairline color that defines structure |
| Current | `#2b3a48` | `--color-current` | Secondary borders, muted icon strokes, subtle dividers between content blocks |
| Kelp | `#455a6b` | `--color-kelp` | Tertiary borders, inactive nav items — barely visible structural lines |
| Silt | `#5c7488` | `--color-silt` | Muted body text, placeholder content, secondary metadata |
| Slate Tide | `#7690a3` | `--color-slate-tide` | Button borders, icon strokes, secondary text, ghost button outlines |
| Sea Fog | `#93aabb` | `--color-sea-fog` | Nav text, body descriptions, helper text — the workhorse readable gray |
| Mist Spray | `#adc0cd` | `--color-mist-spray` | Subdued body copy, supplementary text, less-emphasized paragraphs |
| Foam | `#c9d7e0` | `--color-foam` | Light body text, medium-emphasis paragraphs, secondary headings |
| Shell | `#e3ebf0` | `--color-shell` | High-emphasis body text, dense data labels, the default text tone across most UI |
| Surf White | `#ffffff` | `--color-surf-white` | Primary action button fill, headings, nav active state — the highest contrast color, reserved for elements that must command attention |
| Bioluminescence | `#3fd8c9` | `--color-bioluminescence` | Live-data indicators, "stable" status, category labels — the primary chromatic accent |
| Coral Alert | `#ff7a5c` | `--color-coral-alert` | Critical index states, ALERT_DISPATCHED badges, high-risk map markers — the only warm color, reserved for genuine escalation |
| Signal Gradient | `linear-gradient(103deg, rgb(63, 216, 201), rgb(210, 255, 248) 40%, rgb(63, 216, 201) 70%, rgba(63, 216, 201, 0))` | `--color-signal-gradient` | Timeline/index chart line stroke, live-pulse accent — a cyan-to-white gradient that brings the only color energy to data visualizations |

## Tokens — Typography

### Space Grotesk — Display and heading sans — used for the ecosystem index number, section titles, and hero headlines at 28px and above. Slightly wide geometric letterforms with a technical, chart-legend character give large numerals instrument-panel authority without editorial flourish. This is the primary brand signature — it separates OceanPulse from generic dashboard templates. · `--font-space-grotesk`
- **Substitute:** IBM Plex Sans, General Sans, Söhne
- **Weights:** 400, 500
- **Sizes:** 28px, 44px, 52px, 64px, 88px
- **Line height:** 1.0–1.38
- **Letter spacing:** -0.0050em
- **Role:** Display and heading sans — used exclusively for the ecosystem index number, hero headlines, and section titles at 28px and above.

### Inter — UI sans — body, nav, buttons, labels, links, form fields, and the 48px subhead level. The 300 weight appears on 18px body for whisper-quiet secondary copy; 500 dominates for medium-emphasis text and button labels; 600 is reserved for small-caps status labels. · `--font-inter`
- **Substitute:** Inter (self-hosted via Google Fonts)
- **Weights:** 300, 400, 500, 600, 700
- **Sizes:** 12px, 13px, 14px, 15px, 16px, 18px, 20px, 24px, 48px
- **Line height:** 1.0–1.56
- **Letter spacing:** -0.0400em, -0.0250em, -0.0200em, -0.0130em, -0.0070em, 0.0100em
- **Role:** UI sans — body, nav, buttons, labels, links, form fields, and dense data-table cells.

### Type Scale

| Role | Size | Line Height | Letter Spacing | Token |
|------|------|-------------|----------------|-------|
| eyebrow | 13px | 1 | -0.26px | `--text-eyebrow` |
| body-xs | 16px | 1.5 | — | `--text-body-xs` |
| body-sm | 18px | 1.38 | -0.36px | `--text-body-sm` |
| body | 20px | 1.38 | -0.8px | `--text-body` |
| subheading | 24px | 1 | -0.31px | `--text-subheading` |
| heading-sm | 44px | 1.38 | 0.44px | `--text-heading-sm` |
| heading | 52px | 1.13 | 0.52px | `--text-heading` |
| heading-lg | 64px | 1.13 | 0.64px | `--text-heading-lg` |
| display | 88px | 1 | 0.88px | `--text-display` |

## Tokens — Spacing & Shapes

**Density:** compact

### Spacing Scale

| Name | Value | Token |
|------|-------|-------|
| 4 | 4px | `--spacing-4` |
| 6 | 6px | `--spacing-6` |
| 8 | 8px | `--spacing-8` |
| 9 | 9px | `--spacing-9` |
| 10 | 10px | `--spacing-10` |
| 12 | 12px | `--spacing-12` |
| 14 | 14px | `--spacing-14` |
| 16 | 16px | `--spacing-16` |
| 20 | 20px | `--spacing-20` |
| 22 | 22px | `--spacing-22` |
| 24 | 24px | `--spacing-24` |
| 32 | 32px | `--spacing-32` |
| 40 | 40px | `--spacing-40` |
| 48 | 48px | `--spacing-48` |
| 105 | 105px | `--spacing-105` |
| 224 | 224px | `--spacing-224` |

### Border Radius

| Element | Value |
|---------|-------|
| nav | 2px |
| tags | 9999px |
| cards | 10px |
| icons | 9999px |
| inputs | 9999px |
| buttons | 9999px |

### Shadows

| Name | Value | Token |
|------|-------|-------|
| subtle | `rgba(255, 255, 255, 0.15) 0px 0px 0px 1px` | `--shadow-subtle` |

### Layout

- **Page max-width:** 1216px
- **Section gap:** 160px
- **Card padding:** 24px
- **Element gap:** 8px

## Components

### Primary Action Button
**Role:** Highest-emphasis interactive element — e.g. "Run Analysis"

Pill-shaped, 9999px radius. White (#ffffff) fill, black (#000000) text at 14px Inter weight 500. Padding 10px 20px. No border. Reserve for the single most important action per screen.

### Ghost Outline Button
**Role:** Secondary action — paired with the primary in the header

Transparent fill with 1px white (#ffffff) border, 9999px radius. White text at 14px Inter weight 500. Padding 10px 20px. Used for "Sign in" and less-critical actions.

### Region Filter Pill
**Role:** Region/date-range/data-layer filter chip

Transparent background, 1px border in #7690a3, 9999px radius, padding 6px 10px. White text at 12–14px Inter. Subdued and cool-toned so it reads as a filter control, not a call to action.

### Ecosystem Index Card
**Role:** Showcase the fused index score in the hero/dashboard

Dark surface (#080d14) with 10px radius. No visible border. Contains a region header, index level badge (Stable/Watch/Stressed/Critical), the index number in Space Grotesk, a period filter pill, and a cyan gradient trend line. The chart line uses the signal gradient (linear-gradient 103deg) as its stroke — this is the only place the accent animates the page, aside from live-data pulses.

### Contributing Factors List
**Role:** Dense explainability panel

Right-side panel next to the Ecosystem Index Card, 10px radius, transparent fill. Contains rows with factor-type icon wells (thermometer for SST anomaly, fish for CPUE decline, DNA helix for eDNA signal, ship for vessel density), factor label, and a small severity indicator right-aligned. Dense vertical rhythm with 2px internal padding.

### Species Match Card
**Role:** eDNA/metabarcoding result display

10px radius, transparent fill. Top: taxon name in 18–20px Inter weight 500 white. Below: match-confidence bar, and a Bioluminescence-colored (#3fd8c9) status tag for "common" matches or a Coral Alert (#ff7a5c) tag for "rare/invasive" matches. Sample date and reference-database source in muted text at bottom. No border — cards separate through whitespace alone.

### Region Map Panel
**Role:** Primary geospatial visualization

Full-bleed map panel with 10px radius, dark basemap. Region boundary highlighted in Bioluminescence (#3fd8c9) when stable/watch, and Coral Alert (#ff7a5c) when stressed/critical. Vessel-density and species-occurrence layers toggle via a floating layer-control chip in the top-right corner.

### Timeline Chart Card
**Role:** Ecosystem-index-over-time visualization

10px radius, transparent fill, no border. Signal-gradient line on a hairline-gridded background. Event markers (data-source changes, alert dispatches) shown as small dots with hover tooltips. Axis labels in muted Inter at 12–13px.

### Alert Status Badge
**Role:** NO_ALERT / ALERT_DISPATCHED indicator

Small pill, 9999px radius, 1px border, 2px vertical padding. NO_ALERT: sage-green border and text. ALERT_DISPATCHED: Coral Alert (#ff7a5c) border and text at 12px Inter weight 500. The only two chromatic states on an otherwise monochrome badge system.

### Data Source Label
**Role:** Provenance/status tag on every data element

Transparent fill, 1px border in #2b3a48, 9999px radius, padding 4px 8px. Text at 11–12px Inter weight 500 in #93aabb: "LIVE", "CACHED", "HISTORICAL", or "DEMO". Always visible — never hidden behind a tooltip.

### Email/Region Search Input
**Role:** Hero/dashboard region search field

Transparent fill, 1px white (#ffffff) border, 9999px radius. Padding 10px 10px 10px 20px. Placeholder text in #7690a3. Pairs with the Primary Action Button as a single visual unit.

### Navigation Link
**Role:** Top-level menu item

No background, no border. Text at 14px Inter in #93aabb (inactive) or #ffffff (active/hover). Dropdown chevron for items with sub-menus (Data, Regions, Species, About). Padding 6px 10px for click target. 2px underline radius on hover indicators.

### Status Badge — Stable
**Role:** Positive ecosystem-state indicator in tables

Small pill, transparent fill with 1px sage-toned border. Text in sage at 12px Inter weight 500. 9999px radius, 2px vertical padding. Desaturated sage so it reads on dark without vibrating.

### Stat Display
**Role:** Large numerical proof point (e.g. "1,200+ regions monitored")

Number in 28–44px Space Grotesk weight 400, white. Caption below in 14px Inter weight 400 in #93aabb. The geometric sans numeral gives statistics a technical, instrument-panel gravitas.

### Data Table Row
**Role:** Species list, region list, or timeline event table

Transparent fill, 1px bottom border in #1a2530. No row padding between cells — density is high. Column headers in #93aabb at 14px. Cell values in #e3ebf0 at 14–15px. Right-aligned numerics. The table relies on hairline dividers, not card containers.

## Do's and Don'ts

### Do
- Use Space Grotesk for the ecosystem index number and all headings at 28px and above.
- Set body text at 16px Inter weight 400 with line-height 1.5 in #e3ebf0 (Shell) — this is the default readable tone.
- Use the white (#ffffff) filled pill button exclusively for the single most important action on each screen.
- Apply Bioluminescence (#3fd8c9) to live-data indicators and stable-state signals; apply Coral Alert (#ff7a5c) only to genuine critical/alert states.
- Use 1px borders in #1a2530 or #2b3a48 for card and table edges; never use drop shadows for elevation.
- Always show a Data Source Label on any element that renders external or cached data.
- Use 9999px border-radius for all buttons, inputs, tags, and status indicators; use 10px for cards and 2px for nav underlines.

### Don't
- Don't substitute Inter for Space Grotesk on the index number or hero headline — the scale contrast is the interface's clearest visual hierarchy cue.
- Don't introduce a third chromatic color — Bioluminescence (stable/live) and Coral Alert (critical) are the only two accents, and they carry meaning, not decoration.
- Don't use Coral Alert on anything that isn't an actual CRITICAL index state or ALERT_DISPATCHED badge — reusing it elsewhere erodes its warning signal.
- Don't add drop shadows to cards, modals, or popovers — use surface color steps and 1px borders instead.
- Don't set body text larger than 20px in Inter — larger sizes belong in Space Grotesk.
- Don't apply the signal gradient outside chart/live-pulse contexts — it is reserved for the index trend line and live-data indicators.
- Don't hide data provenance — every data-derived element needs a visible LIVE/CACHED/HISTORICAL/DEMO label.

## Surfaces

| Level | Name | Value | Purpose |
|-------|------|-------|---------|
| 0 | Abyss | `#05080c` | Page canvas, page-level background |
| 1 | Trench | `#080d14` | Card surfaces, contained content blocks |
| 2 | Deep Water | `#101821` | Elevated panels, dropdown surfaces, input backgrounds |
| 3 | Reef Shadow | `#1a2530` | Borders, dividers, floating UI elements, icon wells |

## Elevation

- **Icon rings:** `rgba(255, 255, 255, 0.15) 0px 0px 0px 1px`

## Imagery

Photography and illustration are documentary and technical: satellite imagery, bathymetric maps, underwater survey photos, and vessel/sensor equipment shots. Images fill card frames edge-to-edge with no padding. A dark gradient overlay is applied to the bottom portion of any card with text over imagery, for legibility. The aesthetic is "research vessel logbook meets satellite console" — factual, slightly desaturated, never stock-photo polished or overly dramatic (see the loading-message guidance in the product's own tooling: keep sensitive-topic copy plain and factual). Product UI is shown in dark mode at full opacity, floating above the page on subtle dark surfaces — the map and index card are the centerpiece. Icons are monochrome with 1px strokes in #2b3a48 or #7690a3, filled with accent color only to indicate state (stable/critical).

## Layout

Max-width 1216px centered content with 160px vertical section gaps. The primary dashboard view is a full-width dark canvas with a split composition: left-aligned region map and Ecosystem Index Card, and a right-hand column with the Contributing Factors List and Alert Status Badge. Subsequent sections use a single-column centered headline (Space Grotesk at 44–64px) with subtitle in Inter, followed by 3-column card grids for species matches/regions/timeline events. Navigation is a fixed top bar: logo left, center menu (Data, Regions, Species, About), right-aligned Sign in (ghost) and Run Analysis (white filled pill). Footer is a dense multi-column link grid with data-source attributions and legal. The page alternates between content-rich grid sections and full-bleed stat callouts — rhythm is established by generous whitespace, not alternating background colors (the entire page is one continuous #05080a canvas).

## Agent Prompt Guide

Quick Color Reference:
- text: #e3ebf0 (body) / #ffffff (headings, emphasis)
- background: #05080c (page) / #080d14 (card) / #101821 (panel)
- border: #1a2530 (hairline) / #2b3a48 (secondary)
- accent (stable/live): #3fd8c9 (Bioluminescence)
- accent (critical/alert): #ff7a5c (Coral Alert)
- primary action: #ffffff (filled action)
- chart accent: signal gradient (rgb(63,216,201) → rgb(210,255,248))

Example Component Prompts:

1. Create an Ecosystem Index Card: #080d14 background, 10px radius, no border. Top: region name and a level badge (Stable/Watch/Stressed/Critical) using Bioluminescence or Coral Alert border+text. Center: index number in 64px Space Grotesk weight 400 white. Below: a period filter pill and a signal-gradient trend line chart. Bottom: a Data Source Label pill.

2. Create a Contributing Factors List: transparent background, dense rows with 2px vertical padding. Each row: a monochrome icon in a 1px-bordered circular well (#1a2530), factor label in 15px Inter weight 400 #e3ebf0, and a small severity dot right-aligned (Bioluminescence for minor, Coral Alert for major).

3. Create a Species Match Card: 10px radius, transparent fill, no border. Taxon name in 20px Inter weight 500 white. A horizontal confidence bar below (Bioluminescence fill on #1a2530 track). A status tag: Bioluminescence border for "common," Coral Alert border for "rare/invasive." Sample date and reference-database name in #93aabb at 12px.

4. Create an Alert Status Badge: pill shape, 9999px radius, 1px border, 12px Inter weight 500 text, 2px vertical padding. NO_ALERT uses a sage-green border/text; ALERT_DISPATCHED uses #ff7a5c border/text with a small warning icon.

5. Create a data table for species occurrences: transparent background, 1px bottom border in #1a2530 on each row. Column headers in #93aabb at 14px Inter weight 500, cell values in #e3ebf0 at 15px Inter weight 400. Right-aligned numeric columns (match confidence, count). Status column uses a pill badge: 9999px radius, 1px border, 12px Inter weight 500 text.

## Data-Density Type System

The defining structural choice is a single geometric sans (Space Grotesk) reserved for numerals and headings 28px and above, paired with Inter for all UI text below that threshold. This creates a two-tier typographic register: Space Grotesk speaks to the moments that matter most (the index number, section titles), Inter handles everything functional and informational (body, labels, buttons, table cells). Never cross the boundary — the display face never goes below 28px, Inter never goes above 48px. Unlike an editorial system, there is no serif anywhere in this interface — the goal is instrument-panel legibility, not luxury.

## Similar Products

- **Global Fishing Watch** — Shares the dark-canvas geospatial dashboard approach with a single bright accent for vessel/fishing-activity highlighting on a near-black basemap.
- **Windy / Copernicus Marine viewers** — Comparable dense data-layer toggling and muted dark-mode map styling, though those lean more purely cartographic with less card-based explainability UI.
- **Datadog / Grafana** — Similar dark-mode operational-dashboard density, hairline borders over shadows, and a restrained accent-color-for-status-only philosophy.
- **Stripe Dashboard** — Comparable card-grid layouts, pill buttons, and typography discipline, though Stripe's palette is more neutral gray and OceanPulse leans distinctly navy/cyan.

## Quick Start

### CSS Custom Properties

```css
:root {
  /* Colors */
  --color-abyss: #05080c;
  --color-trench: #080d14;
  --color-deep-water: #101821;
  --color-reef-shadow: #1a2530;
  --color-current: #2b3a48;
  --color-kelp: #455a6b;
  --color-silt: #5c7488;
  --color-slate-tide: #7690a3;
  --color-sea-fog: #93aabb;
  --color-mist-spray: #adc0cd;
  --color-foam: #c9d7e0;
  --color-shell: #e3ebf0;
  --color-surf-white: #ffffff;
  --color-bioluminescence: #3fd8c9;
  --color-coral-alert: #ff7a5c;
  --gradient-signal-gradient: linear-gradient(103deg, rgb(63, 216, 201), rgb(210, 255, 248) 40%, rgb(63, 216, 201) 70%, rgba(63, 216, 201, 0));

  /* Typography — Font Families */
  --font-space-grotesk: 'Space Grotesk', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-inter: 'Inter', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;

  /* Typography — Scale */
  --text-eyebrow: 13px;
  --leading-eyebrow: 1;
  --tracking-eyebrow: -0.26px;
  --text-body-xs: 16px;
  --leading-body-xs: 1.5;
  --text-body-sm: 18px;
  --leading-body-sm: 1.38;
  --tracking-body-sm: -0.36px;
  --text-body: 20px;
  --leading-body: 1.38;
  --tracking-body: -0.8px;
  --text-subheading: 24px;
  --leading-subheading: 1;
  --tracking-subheading: -0.31px;
  --text-heading-sm: 44px;
  --leading-heading-sm: 1.38;
  --tracking-heading-sm: 0.44px;
  --text-heading: 52px;
  --leading-heading: 1.13;
  --tracking-heading: 0.52px;
  --text-heading-lg: 64px;
  --leading-heading-lg: 1.13;
  --tracking-heading-lg: 0.64px;
  --text-display: 88px;
  --leading-display: 1;
  --tracking-display: 0.88px;

  /* Typography — Weights */
  --font-weight-light: 300;
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* Spacing */
  --spacing-4: 4px;
  --spacing-6: 6px;
  --spacing-8: 8px;
  --spacing-9: 9px;
  --spacing-10: 10px;
  --spacing-12: 12px;
  --spacing-14: 14px;
  --spacing-16: 16px;
  --spacing-20: 20px;
  --spacing-22: 22px;
  --spacing-24: 24px;
  --spacing-32: 32px;
  --spacing-40: 40px;
  --spacing-48: 48px;
  --spacing-105: 105px;
  --spacing-224: 224px;

  /* Layout */
  --page-max-width: 1216px;
  --section-gap: 160px;
  --card-padding: 24px;
  --element-gap: 8px;

  /* Border Radius */
  --radius-sm: 2px;
  --radius-lg: 10px;
  --radius-full: 9999px;

  /* Named Radii */
  --radius-nav: 2px;
  --radius-tags: 9999px;
  --radius-cards: 10px;
  --radius-icons: 9999px;
  --radius-inputs: 9999px;
  --radius-buttons: 9999px;

  /* Shadows */
  --shadow-subtle: rgba(255, 255, 255, 0.15) 0px 0px 0px 1px;

  /* Surfaces */
  --surface-void: #05080c;
  --surface-card: #080d14;
  --surface-panel: #101821;
  --surface-floating: #1a2530;
}
```

### Tailwind v4

```css
@theme {
  /* Colors */
  --color-abyss: #05080c;
  --color-trench: #080d14;
  --color-deep-water: #101821;
  --color-reef-shadow: #1a2530;
  --color-current: #2b3a48;
  --color-kelp: #455a6b;
  --color-silt: #5c7488;
  --color-slate-tide: #7690a3;
  --color-sea-fog: #93aabb;
  --color-mist-spray: #adc0cd;
  --color-foam: #c9d7e0;
  --color-shell: #e3ebf0;
  --color-surf-white: #ffffff;
  --color-bioluminescence: #3fd8c9;
  --color-coral-alert: #ff7a5c;

  /* Typography */
  --font-space-grotesk: 'Space Grotesk', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-inter: 'Inter', ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;

  /* Typography — Scale */
  --text-eyebrow: 13px;
  --leading-eyebrow: 1;
  --tracking-eyebrow: -0.26px;
  --text-body-xs: 16px;
  --leading-body-xs: 1.5;
  --text-body-sm: 18px;
  --leading-body-sm: 1.38;
  --tracking-body-sm: -0.36px;
  --text-body: 20px;
  --leading-body: 1.38;
  --tracking-body: -0.8px;
  --text-subheading: 24px;
  --leading-subheading: 1;
  --tracking-subheading: -0.31px;
  --text-heading-sm: 44px;
  --leading-heading-sm: 1.38;
  --tracking-heading-sm: 0.44px;
  --text-heading: 52px;
  --leading-heading: 1.13;
  --tracking-heading: 0.52px;
  --text-heading-lg: 64px;
  --leading-heading-lg: 1.13;
  --tracking-heading-lg: 0.64px;
  --text-display: 88px;
  --leading-display: 1;
  --tracking-display: 0.88px;

  /* Spacing */
  --spacing-4: 4px;
  --spacing-6: 6px;
  --spacing-8: 8px;
  --spacing-9: 9px;
  --spacing-10: 10px;
  --spacing-12: 12px;
  --spacing-14: 14px;
  --spacing-16: 16px;
  --spacing-20: 20px;
  --spacing-22: 22px;
  --spacing-24: 24px;
  --spacing-32: 32px;
  --spacing-40: 40px;
  --spacing-48: 48px;
  --spacing-105: 105px;
  --spacing-224: 224px;

  /* Border Radius */
  --radius-sm: 2px;
  --radius-lg: 10px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-subtle: rgba(255, 255, 255, 0.15) 0px 0px 0px 1px;
}
```
