# OceanPulse AI — AI Coding Instructions

## Project Goal
Build a reliable hackathon MVP that unifies oceanographic, fisheries, and molecular biodiversity (eDNA) data into a single AI-driven platform. The platform ingests heterogeneous marine data, extracts ecological/biodiversity signals, explains what is driving them, and surfaces an actionable alert when an ecosystem-stress or fisheries-risk threshold is crossed.

Core story:
INGEST → HARMONIZE → ANALYZE → EXPLAIN → ALERT

This is a decision-support and research tool, NOT a definitive scientific, regulatory, or legal verdict.

## Architecture
oceanpulse-ai/
├── frontend/        # React + Vite + TypeScript + Tailwind
├── backend/         # FastAPI + Pydantic + PostgreSQL/PostGIS
├── ml/              # taxonomic matching + anomaly/stock models + fusion engine
├── data-pipeline/   # connectors: Argo floats, satellite, AIS, eDNA uploads
├── docs/
├── .env.example
├── CLAUDE.md
└── implementation_plan.md

## Technology Stack
Frontend:
- React
- Vite
- TypeScript
- Tailwind CSS
- Recharts
- Leaflet or Mapbox GL JS (geospatial map layer)

Backend:
- Python
- FastAPI
- Pydantic
- PostgreSQL + PostGIS (spatial queries)

ML:
- Scikit-learn
- XGBoost (fisheries stock / CPUE trend classification)
- IsolationForest (ecosystem anomaly detection)
- Taxonomic reference matcher (embedding/lookup-based species matching for eDNA/metabarcoding reads — not a full sequence aligner)

Data Sources (public/open only):
- Argo float profiles (temperature, salinity, depth)
- NOAA / Copernicus Marine satellite data (SST, chlorophyll-a)
- GBIF / OBIS biodiversity occurrence records
- AIS-derived vessel density (fisheries pressure proxy)
- User-uploaded eDNA / metabarcoding sample files (CSV/FASTA)

## Core Flow
Region or sample query
→ ingest oceanographic + fisheries + molecular records
→ spatial/temporal feature harmonization
→ taxonomic matcher + anomaly model + rule engine
→ Insight Fusion Engine
→ ecosystem index 0–100
→ explainable factors + timeline
→ Map/Dashboard visualization
→ Alert Gate
→ NO_ALERT / ALERT_DISPATCHED

## Ecosystem Index Levels
0–29   STABLE
30–59  WATCH
60–79  STRESSED
80–100 CRITICAL

Never present outputs as a confirmed scientific or regulatory conclusion. Use language such as:
- elevated ecological stress signals
- pattern consistent with declining biodiversity
- indicative of possible stock depletion
- molecular signal suggests presence of [taxon] (match confidence X%)

## Reliability Rules
The app must remain demoable if external dependencies fail.

Data fallback:
1. Live API data
2. Cached data
3. Historical dataset
4. Demo/sample dataset

Always label the source/status of non-live data.

ML fallback:
1. Trained classifier/matcher
2. Similarity/heuristic match
3. Rule-based scoring
4. Demo scenario

Never fabricate satellite readings, vessel positions, sequencing/taxonomic matches, model metrics, or live data.

## Data & Domain Rules
- Public/open datasets only — no proprietary or restricted data without explicit source labeling.
- Never present an eDNA/metabarcoding species match as certain — always show a confidence/match score.
- Respect rate limits of external APIs (NOAA, Copernicus, GBIF, OBIS, AIS providers).
- All geospatial records must carry a coordinate reference system and timestamp.
- Fisheries stock outputs must state the data vintage/assessment period.
- Explicitly flag low-confidence or sparse-data regions in the UI rather than hiding the gap.
- Never request, store, or expose vessel operator PII beyond public AIS identifiers.

## Alert Gate MVP
Prioritize one reliable protected flow:
Region Analysis → Ecosystem Index → Alert Gate → NO_ALERT / ALERT_DISPATCHED

Do not build multiple alert/action types unless the core flow is already working.

Example:
Index 45 < threshold 70 → NO_ALERT
Index 87 > threshold 70 → ALERT_DISPATCHED

## Demo Scenarios
Healthy Reef:
22 / STABLE / NO_ALERT

Declining Fishery:
55 / WATCH / NO_ALERT

Coral Bleaching Event:
88 / CRITICAL / ALERT_DISPATCHED

The Coral Bleaching Event scenario is the primary judge demo:
28 → warming and biodiversity-loss signals accumulate → 88 → Alert Gate → ALERT_DISPATCHED.

## Explainability
Every meaningful index change should have a reason.

Example factors:
- sea surface temperature anomaly
- declining catch-per-unit-effort (CPUE)
- reduced eDNA species richness
- detected rare or invasive taxon
- vessel-density spike (possible overfishing pressure)
- harmful algal bloom indicator

Show index, level, confidence, factors, timeline, map layer, and data source for every result.

## API Contract
Implement:
GET  /health
POST /api/analyze
GET  /api/region/{id}
GET  /api/insight/{id}
GET  /api/timeline/{id}
GET  /api/species/{id}
GET  /api/edna/matches/{sample_id}
POST /api/demo/analyze

Validate region IDs/coordinates and sample inputs; return useful error messages.

## Coding Style
- TypeScript: strict typing; avoid `any` unless unavoidable.
- Python: type hints, Pydantic models, small functions.
- Keep functions/modules small and focused.
- Prefer explicit names over clever abstractions.
- Avoid unnecessary dependencies.
- Do not rewrite working code without a reason.
- Preserve existing features.
- Keep frontend components modular.
- Keep API schemas stable once implemented.
- Add comments only where they explain non-obvious scientific/domain logic.

## File Size / Complexity Limits
Prefer:
- Frontend component: ≤ 250 lines
- Backend module: ≤ 300 lines
- ML module: ≤ 300 lines where practical
- Avoid giant single-file components.
- If a file grows beyond these limits, split it by responsibility.

These are guidelines, not reasons to create pointless abstractions.

## Development Rules
Before editing:
1. Inspect the existing structure.
2. Identify the smallest set of files required.
3. Check whether functionality already exists.
4. Preserve working code.

After editing:
1. Run the relevant tests.
2. Run type/build checks.
3. Check the API starts.
4. Check the frontend starts.
5. Check ML pipeline import/run if ML changed.
6. Fix the actual error rather than applying random changes.

## Priority Order
1. Insight Fusion Engine (rule-based core)
2. Data ingestion with demo/sample data
3. Explainable AI (factors + timeline)
4. Dashboard + Map
5. Alert Gate
6. eDNA / molecular biodiversity matching
7. Fisheries stock trend model
8. Live API integration (Argo / Copernicus / GBIF / OBIS / AIS)
9. Advanced ML (embeddings, forecasting)
10. Extras (exports, notifications)

## Do Not Over-Engineer
Do not implement full genomic sequence aligners, real-time satellite ingestion at scale, production alerting infrastructure, or multi-agency integrations in the MVP unless the core demo is already reliable.

## Required Demo Integrity
The judge must be able to understand this within 30 seconds:

SELECT REGION
→ AI FUSES OCEAN + FISHERIES + eDNA DATA
→ ECOSYSTEM INDEX RISES
→ REASONS ARE SHOWN
→ MAP HIGHLIGHTS THE AREA
→ TIMELINE SHOWS THE ESCALATION
→ ALERT GATE DISPATCHES AN ALERT

## Commands
Use the actual commands documented by package manifests and README files. Do not invent commands. If the project is not initialized yet, establish minimal commands for:
- frontend dev/build
- backend run/test
- ML test/run
- data-pipeline run/test

## Output Expectations
When implementing a feature, report:
- What is being built
- Files changed
- Important implementation decisions
- Exact commands to run
- Test result
- One next logical step

Do not claim something is live, deployed, trained, or tested unless it actually is.
