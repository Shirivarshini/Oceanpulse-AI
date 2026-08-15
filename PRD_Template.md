# **Product requirements document (PRD)**

## OceanPulse AI — AI-Driven Unified Data Platform for Oceanographic, Fisheries, and Molecular Biodiversity Insights

This PRD follows the standard problem → solution → MVP structure so it can be handed directly to an AI coding assistant alongside `CLAUDE.md` and `implementation_plan.md`.

# 1. The problem

What pain do users feel when this product doesn't exist?

| Marine researchers, fisheries managers, and conservation NGOs currently pull oceanographic readings, fisheries catch/effort data, and molecular biodiversity (eDNA) results from separate, disconnected systems — government portals, spreadsheets, lab reports, and satellite dashboards. Correlating a temperature anomaly with a declining catch rate and a drop in species richness from an eDNA sample requires manually exporting data from three or more tools and joining it by hand. By the time a pattern is spotted, the underlying event (a bleaching episode, an overfishing spike, an invasive-species incursion) may already be well underway. Small teams and under-resourced agencies waste days on data wrangling instead of acting on the signal. |
| :---- |

# 2. Existing solutions

How are people solving this today, and what are they missing?

| 1. **Government/agency ocean data portals** (e.g. national ocean services, satellite data portals) — provide raw oceanographic data but no fisheries or molecular biodiversity context, and no fused risk scoring.  2. **Fisheries stock assessment spreadsheets/reports** — authoritative but slow-moving, often annual, and disconnected from real-time environmental signals.  3. **Standalone eDNA/metabarcoding lab pipelines** — produce species-match results but stop there; they don't connect findings back to location-specific ocean or fisheries context, and results are hard to interpret without domain expertise.  What's missing across all three: no single place that fuses these three data types, explains *why* a region's ecological status changed, and turns that into a clear, actionable signal. |
| :---- |

# 3. Your target user

Who is this for, and what are they trying to achieve?

| Marine researchers, regional fisheries managers, and conservation/NGO analysts monitoring a coastal or offshore region. They need to know, quickly and with evidence, whether a region's ecosystem is stable or showing early warning signs — so they can prioritize field visits, flag areas for protection, or escalate to the right authority before a situation becomes irreversible. They care about defensible, source-labeled data (not black-box claims), and they need results that are understandable to non-ML-specialist stakeholders. |
| :---- |

# 4. Your solution

What does your product do, and what are the two or three key benefits?

| OceanPulse AI is a unified platform that ingests oceanographic, fisheries, and molecular biodiversity (eDNA) data for a selected region, fuses it into a single explainable ecosystem index, and dispatches an alert when the index crosses a configurable risk threshold. Key benefits: (1) one dashboard instead of three disconnected data sources, (2) every score change comes with plain-language, evidence-backed factors and a timeline — not a black-box number, (3) a built-in demo/fallback mode means the tool keeps working for a presentation or a field visit even if a live API is down. |
| :---- |

# 5. The minimum version (MVP)

What are the key features someone needs to actually use this?

| 1. Region selector with an interactive map showing the fused ecosystem index (Stable/Watch/Stressed/Critical). 2. Insight Fusion Engine that combines oceanographic (temperature/salinity anomalies), fisheries (catch-per-unit-effort trend), and molecular (eDNA species-match) signals into one 0–100 index with a confidence score. 3. Explainability panel: contributing factors plus a timeline showing how the index changed and why. 4. eDNA/metabarcoding sample upload with confidence-scored taxonomic matches and rare/invasive-species flags. 5. Alert Gate: a configurable threshold that dispatches NO_ALERT or ALERT_DISPATCHED, with a clear reason and rejection of stale data. |
| :---- |

# 6. Appendix — extra details

Keep this separate from the core PRD. Add it to your prompt after the AI understands your main goal.

### Design ideas or visual references

| Deep-ocean palette: near-black/deep-navy canvas, teal/cyan primary accent, a single bioluminescent-cyan gradient reserved for index/trend charts. Clean sans-serif UI type for data density, with a display serif or heavier sans reserved for the ecosystem index number and section headings. See `DESIGN.md` for the full token/component reference. |
| :---- |

### Technical notes or integrations

| Argo float API (ocean profiles), NOAA/Copernicus Marine (SST, chlorophyll-a), GBIF/OBIS (biodiversity occurrence records), AIS-derived vessel density (fisheries pressure proxy), user-uploaded eDNA/metabarcoding CSV or FASTA files. PostgreSQL with PostGIS for spatial/temporal queries. All live-data dependencies must have a cached/historical/demo fallback per `CLAUDE.md`. |
| :---- |

### Pricing model

| Not applicable for the hackathon MVP — the platform targets research institutions, fisheries agencies, and NGOs; a future version could offer institutional/agency licensing rather than individual subscriptions. |
| :---- |

### Go-to-market notes

| Lead with marine research institutions, coastal fisheries management agencies, and ocean-conservation NGOs. Distribution via academic/conservation conferences, hackathon/grant program visibility, and direct outreach to regional fisheries authorities already using open ocean data portals. |
| :---- |
