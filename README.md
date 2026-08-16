# OceanPulse AI

### AI-Driven Unified Data Platform for Oceanographic, Fisheries & Molecular Biodiversity Insights

OceanPulse AI is a decision-support platform that unifies **oceanographic, fisheries, and molecular biodiversity (eDNA)** data into one explainable ecosystem-risk view.

It is designed to help marine researchers, fisheries managers, and conservation teams identify **early warning signals of ecosystem stress** without manually combining data from multiple disconnected systems.

> **INGEST → HARMONIZE → ANALYZE → EXPLAIN → ALERT**

OceanPulse is a research and decision-support tool. Its outputs are **not definitive scientific, regulatory, or legal conclusions**.

---

## Problem

Marine ecosystem information is distributed across:

* Oceanographic data portals
* Fisheries reports and datasets
* Satellite observations
* Biodiversity databases
* eDNA/metabarcoding laboratory results
* Vessel-density/AIS data

Connecting these datasets manually makes it difficult to quickly identify relationships between environmental changes, fisheries pressure, and biodiversity loss.

OceanPulse brings these signals together into a single platform.

---

## Solution

For a selected marine region, OceanPulse:

1. Ingests oceanographic, fisheries, and biodiversity data.
2. Harmonizes the data spatially and temporally.
3. Extracts environmental, fisheries, and molecular signals.
4. Calculates an explainable **0–100 Ecosystem Index**.
5. Shows the factors contributing to the score.
6. Displays how the score changed over time.
7. Visualizes the region on an interactive map.
8. Runs an Alert Gate against a configurable threshold.
9. Dispatches either `NO_ALERT`, `ALERT_DISPATCHED`, or blocks stale analyses.

The platform remains usable when external data sources are unavailable through:

**LIVE → CACHED → HISTORICAL → DEMO**

---

## Core Features

### Ecosystem Index

|  Score | Status     |
| -----: | ---------- |
|   0–29 | `STABLE`   |
|  30–59 | `WATCH`    |
|  60–79 | `STRESSED` |
| 80–100 | `CRITICAL` |

The index combines signals from:

* Oceanographic conditions
* Fisheries/CPUE trends
* Molecular biodiversity
* Vessel-density pressure
* Other supported ecological indicators

### Explainability

Every meaningful index change includes contributing factors such as:

* Sea-surface-temperature anomaly
* CPUE decline
* Reduced eDNA species richness
* Rare/invasive taxon detection
* Vessel-density increase
* Other supported ecological indicators

The system should explain results using evidence-backed language rather than presenting a black-box prediction.

### eDNA / Molecular Biodiversity

The platform supports CSV/FASTA sample inputs and provides:

* Taxonomic matches
* Match confidence
* Species richness
* Rare-species flags
* Invasive-species flags
* Low-quality/contamination indicators

eDNA matches are **never presented as scientifically certain**.

### Interactive Map

The dashboard provides a geographic view of:

* Selected region
* Ecosystem status
* Species occurrences
* Vessel-density layers where available
* Other supported spatial signals

### Alert Gate

The Alert Gate evaluates:

```text
index < threshold
        ↓
NO_ALERT
```

```text
index >= threshold
        ↓
ALERT_DISPATCHED
```

Stale analyses are blocked:

```text
stale analysis
        ↓
ALERT_BLOCKED_STALE
```

---

## Demo Scenarios

OceanPulse includes three predefined scenarios:

| Scenario          | Index | Level    | Alert              |
| ----------------- | ----: | -------- | ------------------ |
| Healthy Reef      |    22 | STABLE   | `NO_ALERT`         |
| Declining Fishery |    55 | WATCH    | `NO_ALERT`         |
| Coral Bleaching   |    88 | CRITICAL | `ALERT_DISPATCHED` |

### Primary Hackathon Demo

```text
28
 ↓
Warming + biodiversity-loss signals accumulate
 ↓
88
 ↓
CRITICAL
 ↓
Alert Gate
 ↓
ALERT_DISPATCHED
```

The judge should be able to understand the complete product flow within approximately 30 seconds.

---

## Architecture

```text
                    ┌─────────────────┐
                    │    Frontend     │
                    │ React + Vite    │
                    │ TypeScript      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Backend     │
                    │ FastAPI         │
                    │ Pydantic        │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
      ┌─────────────────┐          ┌─────────────────┐
      │ Data Pipeline   │          │ Fusion Engine   │
      │ Ocean/Fisheries │          │ Scoring + ML    │
      │ eDNA/AIS        │          │ Explainability  │
      └─────────────────┘          └────────┬────────┘
                                            │
                                            ▼
                                   ┌─────────────────┐
                                   │   Alert Gate    │
                                   │ NO_ALERT /      │
                                   │ ALERT_DISPATCHED│
                                   └─────────────────┘
```

### Repository Structure

```text
oceanpulse-ai/
├── frontend/
├── backend/
├── ml/
├── data-pipeline/
├── docs/
├── .env.example
├── CLAUDE.md
├── implementation_plan.md
└── README.md
```

---

## Technology Stack

### Frontend

* React
* Vite
* TypeScript
* Tailwind CSS
* Recharts
* Leaflet or Mapbox GL JS

### Backend

* Python
* FastAPI
* Pydantic
* PostgreSQL
* PostGIS

### ML

* Scikit-learn
* XGBoost
* IsolationForest
* Taxonomic reference matcher

### Data Sources

Where practical, OceanPulse can integrate:

* Argo float profiles
* NOAA / Copernicus Marine
* GBIF
* OBIS
* AIS-derived vessel density
* User-uploaded eDNA/metabarcoding files

Public/open data should be preferred.

---

## Data Reliability

External APIs must never become a single point of failure.

The fallback chain is:

```text
LIVE
  ↓
CACHED
  ↓
HISTORICAL
  ↓
DEMO
```

Every data-derived result must expose its source status:

```text
LIVE
CACHED
HISTORICAL
DEMO
```

**Never label cached, historical, or demo data as `LIVE`.**

The system must continue to operate when:

* Ocean APIs are unavailable
* Biodiversity APIs are unavailable
* ML models are unavailable
* External rate limits are reached

---

## ML Reliability

ML is an enhancement, not a dependency.

Preferred fallback:

```text
Trained Model
      ↓
Similarity / Heuristic Match
      ↓
Rule-Based Scoring
      ↓
Demo Scenario
```

The core rule-based Fusion Engine must remain functional without ML.

The system must never fabricate:

* Model metrics
* Satellite readings
* Vessel positions
* Taxonomic matches
* Live measurements
* Scientific conclusions

---

## API

The local backend runs at:

```text
http://localhost:8000
```

### Health

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

### Analyze Region

```http
POST /api/analyze
```

Example request:

```json
{
  "region_id": "gulf-of-mannar",
  "latitude": 9.0,
  "longitude": 79.0,
  "threshold": 70
}
```

### Demo Analysis

```http
POST /api/demo/analyze
```

Example:

```json
{
  "scenario": "coral_bleaching"
}
```

Allowed scenarios:

```text
healthy_reef
declining_fishery
coral_bleaching
```

### Additional Endpoints

```text
GET  /api/region/{id}
GET  /api/insight/{id}
GET  /api/timeline/{id}
GET  /api/species/{id}
GET  /api/edna/matches/{sample_id}
```

The API contract should be treated as stable. Endpoint names, field names, enum values, and response structures should not be changed without coordinating with the team.

---

## Analysis Response

Analysis responses follow this structure:

```json
{
  "analysis_id": "analysis-001",
  "region": {
    "id": "gulf-of-mannar",
    "name": "Gulf of Mannar",
    "latitude": 9.0,
    "longitude": 79.0
  },
  "index": 88,
  "level": "CRITICAL",
  "confidence": 0.91,
  "factors": [],
  "timeline": [],
  "alert": {},
  "sources": {},
  "created_at": "ISO-8601 timestamp"
}
```

---

## Development Roadmap

The project is built incrementally:

```text
1. Project Setup
        ↓
2. Dashboard + Demo Data
        ↓
3. FastAPI Backend
        ↓
4. Insight Fusion Engine
        ↓
5. ML Integration
        ↓
6. Live Data Integration
        ↓
7. eDNA Module
        ↓
8. Fisheries + Alert Gate
        ↓
9. Full Integration
        ↓
10. Demo Reliability
        ↓
11. Testing
        ↓
12. Deployment
        ↓
13. Pitch Polish
```

The implementation plan prioritizes a reliable end-to-end demo before advanced integrations.

---

## Development Principles

### 1. Build the smallest reliable path first

The primary flow is:

```text
Region
 ↓
Multi-Source Analysis
 ↓
Explainability
 ↓
Ecosystem Index
 ↓
Alert Gate
 ↓
ALERT_DISPATCHED
```

### 2. Preserve stable interfaces

Frontend, Backend, Fusion Engine, ML, and Data Pipeline components should communicate through defined interfaces.

### 3. Do not over-engineer

The MVP does not require:

* Full genomic sequence alignment
* Large-scale real-time satellite ingestion
* Production-grade alert infrastructure
* Multi-agency integrations

unless the core demonstration is already reliable.

### 4. Test after changes

After implementation:

```text
Run relevant tests
        ↓
Run build/type checks
        ↓
Verify backend
        ↓
Verify frontend
        ↓
Verify ML/data pipeline if affected
```

---

## Design System

OceanPulse uses a **deep-ocean research-console aesthetic**.

### Primary Surfaces

```text
Abyss       #05080c
Trench      #080d14
Deep Water  #101821
Reef Shadow #1a2530
```

### Accent Colors

```text
Bioluminescence  #3fd8c9
Coral Alert      #ff7a5c
```

Bioluminescence represents live/stable signals.

Coral Alert is reserved for genuine critical/alert states.

### Typography

```text
Headings / Index:
Space Grotesk

UI / Body:
Inter
```

The dashboard uses compact, data-dense layouts with thin borders, dark surfaces, rounded cards, and minimal elevation.

---

## Safety & Scientific Integrity

OceanPulse is a **decision-support and research platform**, not a definitive scientific authority.

Use language such as:

* "elevated ecological stress signals"
* "pattern consistent with declining biodiversity"
* "indicative of possible stock depletion"
* "molecular signal suggests presence of [taxon]"
* "match confidence: X%"

Avoid presenting model outputs as confirmed scientific or regulatory conclusions.

---

## Testing

The project should test:

* Frontend build
* Backend unit tests
* API endpoints
* Fusion Engine
* ML pipeline
* eDNA matcher
* Alert Gate
* Data fallback behavior
* End-to-end integration

Critical Alert Gate tests:

```text
Index 45 + threshold 70
→ NO_ALERT

Index 87 + threshold 70
→ ALERT_DISPATCHED

Stale analysis
→ ALERT_BLOCKED_STALE
```

Critical fallback tests:

```text
Live unavailable
→ Cached

Cached unavailable
→ Historical

Historical unavailable
→ Demo
```

---

## Final Integration Test

The complete system is considered integrated when:

```text
SELECT CORAL BLEACHING
        ↓
POST /api/demo/analyze
        ↓
Fusion Engine
        ↓
Index = 88
        ↓
CRITICAL
        ↓
Factors displayed
        ↓
Timeline displayed
        ↓
Map updated
        ↓
Threshold = 70
        ↓
ALERT_DISPATCHED
```

No developer should need to manually modify frontend data to make the primary demo work.

---

## Definition of Done

OceanPulse AI MVP is complete when:

* [ ] Frontend works
* [ ] Backend works
* [ ] Insight Fusion Engine works
* [ ] Demo mode works without external APIs
* [ ] Explainability works
* [ ] eDNA matching works
* [ ] Alert Gate works
* [ ] Index 88 dispatches an alert at threshold 70
* [ ] Healthy Reef remains `NO_ALERT`
* [ ] Stale analyses are rejected
* [ ] Data source labels are accurate
* [ ] No fabricated live data or metrics are shown
* [ ] Tests pass
* [ ] Full frontend → backend → fusion → alert flow works
* [ ] A judge can understand the product in approximately 30 seconds

---

## Project Story

OceanPulse does not simply display marine data.

It connects the signals.

```text
OCEAN
  +
FISHERIES
  +
eDNA
  ↓
AI FUSION
  ↓
ECOSYSTEM INDEX
  ↓
EXPLAINABLE RISK
  ↓
ACTIONABLE ALERT
```

**OceanPulse AI — turning fragmented marine signals into an explainable early-warning system.**
