# OceanPulse AI — Implementation Plan

## Build Strategy

Build the smallest reliable end-to-end path first. After every phase, verify that the project still runs.

Target demo:
Region → Multi-Source Analysis → Explainability → Ecosystem Index → Alert Gate → ALERT_DISPATCHED

---

## Phase 1 — Project Setup

### Goal
Create the modular repository and development environment.

### Tasks
- [ ] Create `frontend/`
- [ ] Create `backend/`
- [ ] Create `ml/`
- [ ] Create `data-pipeline/`
- [ ] Create `docs/`
- [ ] Add `.env.example`
- [ ] Add root `CLAUDE.md`
- [ ] Add root README
- [ ] Establish frontend/backend/ML/data-pipeline commands

### Done when
- Repository structure exists.
- Frontend starts.
- Backend `/health` works.
- ML environment imports successfully.
- Data-pipeline scripts run against sample data.

---

## Phase 2 — Dashboard + Demo Data

### Goal
Build the complete UI before depending on live external data sources.

### Tasks
- [ ] Header and data-source status bar
- [ ] Region selector / search input
- [ ] Ecosystem index card
- [ ] Index level (Stable/Watch/Stressed/Critical)
- [ ] Confidence indicator
- [ ] Contributing factors list
- [ ] Timeline chart
- [ ] Interactive map (region + species/vessel layers placeholder)
- [ ] Data-source status panel (live/cached/historical/demo)
- [ ] eDNA sample upload / match simulator
- [ ] Healthy Reef / Declining Fishery / Coral Bleaching demo scenarios

### Required demo states
- [ ] 22 STABLE → NO_ALERT
- [ ] 55 WATCH → NO_ALERT
- [ ] 88 CRITICAL → ALERT_DISPATCHED

### Done when
A judge can run the UI without backend dependencies and understand the complete product flow.

---

## Phase 3 — FastAPI Backend

### Goal
Create stable API contracts between frontend and the insight engine.

### Tasks
- [ ] `GET /health`
- [ ] `POST /api/analyze`
- [ ] `GET /api/region/{id}`
- [ ] `GET /api/insight/{id}`
- [ ] `GET /api/timeline/{id}`
- [ ] `GET /api/species/{id}`
- [ ] `GET /api/edna/matches/{sample_id}`
- [ ] `POST /api/demo/analyze`
- [ ] Pydantic request/response schemas
- [ ] Region ID / coordinate / sample-file validation
- [ ] Structured error responses

### Done when
Frontend can consume demo/backend responses through the API rather than hard-coded UI state.

---

## Phase 4 — Insight Fusion Engine

### Goal
Create the deterministic core ecosystem-index pipeline.

### Tasks
- [ ] Define normalized feature schema (ocean, fisheries, molecular)
- [ ] Implement factor-extraction interfaces
- [ ] Implement rule-based scoring
- [ ] Add confidence calculation
- [ ] Add explainability output
- [ ] Add index normalization 0–100
- [ ] Add source/status metadata
- [ ] Add fallback chain

### Fallback
Live → Cached → Historical → Demo

### Done when
The same input produces a stable, explainable index and the engine works without ML.

---

## Phase 5 — ML Integration

### Goal
Add ML without making the product dependent on it.

### Tasks
- [ ] Add XGBoost interface (fisheries stock / CPUE trend)
- [ ] Add IsolationForest interface (ecosystem anomaly)
- [ ] Define model input schema
- [ ] Add model availability detection
- [ ] Combine model outputs in the Insight Fusion Engine
- [ ] Store model version in analysis metadata
- [ ] Add evaluation script
- [ ] Report Precision, Recall, F1, ROC-AUC and false-positive rate only when measured

### Done when
ML improves the index result when available, while rule-based fallback still works.

---

## Phase 6 — Live Ocean, Fisheries & Biodiversity Data

### Goal
Replace demo inputs with public data sources where practical.

### Tasks
- [ ] Configure Argo float API access
- [ ] Configure NOAA / Copernicus Marine satellite access (SST, chlorophyll-a)
- [ ] Configure GBIF / OBIS occurrence-record access
- [ ] Configure AIS-derived vessel-density access if available
- [ ] Read region metadata (bounding box, depth, protected-area status)
- [ ] Extract oceanographic anomaly signals where data is available
- [ ] Add caching
- [ ] Handle API/rate-limit failures
- [ ] Clearly label live vs cached/historical data

### Done when
A supported region can produce real data-derived features without breaking the demo fallback.

---

## Phase 7 — Molecular Biodiversity (eDNA) Module

### Goal
Turn eDNA/metabarcoding sample uploads into taxonomic signals.

### Tasks
- [ ] Implement reference-taxa lookup/matcher (embedding or heuristic-based, not a full aligner)
- [ ] Define sample input schema (CSV/FASTA)
- [ ] Add match confidence scoring
- [ ] Add rare/invasive-taxon flagging
- [ ] Add low-quality/contamination flags
- [ ] Add species-richness calculation
- [ ] Write unit tests
- [ ] Integrate output into the Insight Fusion Engine

### Done when
A sample upload produces labeled, confidence-scored taxonomic matches that feed the index.

---

## Phase 8 — Fisheries Stock Model & Alert Gate

### Goal
Make the AI decision actionable through a configurable alert step.

### Tasks
- [ ] Implement configurable alert threshold
- [ ] Read latest Insight Fusion Engine output
- [ ] Validate index freshness (reject stale data)
- [ ] Implement Alert Gate logic
- [ ] Dispatch NO_ALERT when index is below threshold
- [ ] Dispatch ALERT_DISPATCHED when index is above threshold
- [ ] Add clear reason codes for each decision
- [ ] Emit alert events/log entries
- [ ] Write unit tests
- [ ] Wire the Alert Gate into the backend

### Critical test
```text
Index 45 + threshold 70 → NO_ALERT
Index 87 + threshold 70 → ALERT_DISPATCHED
Stale index → ALERT BLOCKED / flagged stale
```

### Done when
The dashboard can trigger a real Alert Gate decision from a live or demo analysis.

---

## Phase 9 — Full Integration

### Goal
Connect every layer.

### Flow
- [ ] Region entered in frontend
- [ ] Backend ingests ocean/fisheries/molecular data
- [ ] Features generated
- [ ] Insight Fusion Engine produces index
- [ ] Explainability returned
- [ ] Timeline returned
- [ ] eDNA matches attached where available
- [ ] Alert Gate evaluates the index
- [ ] Frontend displays index, map, timeline, and alert status

### Done when
The entire flow works from one UI action without manual backend intervention.

---

## Phase 10 — Demo Reliability

### Goal
Make the hackathon demo resilient.

### Tasks
- [ ] Test with no satellite/ocean API
- [ ] Test with no GBIF/OBIS access
- [ ] Test with ML disabled
- [ ] Test with backend unavailable
- [ ] Test invalid region/coordinates
- [ ] Test stale index
- [ ] Test malformed eDNA upload
- [ ] Verify demo scenarios always work
- [ ] Add loading/error states
- [ ] Add source labels

### Done when
The main demo cannot fail simply because an external API is unavailable.

---

## Phase 11 — Testing and Evaluation

### Tests
- [ ] Frontend build
- [ ] Backend unit tests
- [ ] Insight Fusion Engine tests
- [ ] ML pipeline tests
- [ ] eDNA matcher tests
- [ ] API integration tests
- [ ] End-to-end happy path

### Evaluation
- [ ] Precision
- [ ] Recall
- [ ] F1
- [ ] ROC-AUC
- [ ] False-positive rate
- [ ] Early-warning lead time
- [ ] Alert Gate dispatch accuracy
- [ ] No-alert accuracy

Never invent evaluation numbers.

---

## Phase 12 — Deployment

### Tasks
- [ ] Deploy frontend
- [ ] Deploy backend
- [ ] Configure PostgreSQL/PostGIS
- [ ] Configure data-pipeline scheduled jobs
- [ ] Configure environment variables
- [ ] Verify external API credentials/limits
- [ ] Verify frontend/backend URLs
- [ ] Run production smoke test

### Done when
A clean browser session can run the complete demo.

---

## Phase 13 — Pitch Polish

### Tasks
- [ ] Make the ecosystem index card visually dominant
- [ ] Make the 28 → 88 escalation obvious
- [ ] Make reasons immediately readable
- [ ] Show "Index fused from ocean + fisheries + eDNA data"
- [ ] Show the alert threshold
- [ ] Show "🚨 ALERT DISPATCHED"
- [ ] Add live map highlight when available
- [ ] Clearly label demo/historical/synthetic data
- [ ] Remove placeholder metrics
- [ ] Verify 30-second judge experience

### Final demo script

```text
1. Select Coral Bleaching Event demo.
2. Start at Index 28.
3. Show warming and biodiversity-loss signals.
4. Show index escalating to 88.
5. Show contributing factors and timeline.
6. Alert Gate reads 88 > 70.
7. Alert is DISPATCHED.
8. Explain: OceanPulse does not just report data; it fuses ocean, fisheries, and molecular
   signals into one actionable early-warning system.
```

---

## Definition of Done

The MVP is complete when:

- [ ] Frontend works
- [ ] Backend works
- [ ] Insight Fusion Engine works
- [ ] Demo mode works without external APIs
- [ ] Explainability works
- [ ] eDNA matching module works
- [ ] Alert Gate works
- [ ] Index 88 dispatches an alert at threshold 70
- [ ] Healthy Reef scenario stays NO_ALERT
- [ ] Stale indices are rejected
- [ ] No fabricated live data or metrics are shown
- [ ] Tests pass
- [ ] A judge can understand the product in 30 seconds
