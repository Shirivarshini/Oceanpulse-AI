# OceanPulse AI — API Contract

## 1. Purpose

This document defines the exact communication format between:

**Frontend → Backend → Fusion Engine → Alert Gate**

All four team members must follow this contract. Do not change field names or response structures without informing the team.

## 2. Base URL

Local backend:

```text
http://localhost:8000
```

Production:

```text
<DEPLOYED_BACKEND_URL>
```

## 3. Common Response Structure

Analysis responses use:

```json
{
  "analysis_id": "string",
  "region": {
    "id": "string",
    "name": "string",
    "latitude": 0.0,
    "longitude": 0.0
  },
  "index": 0,
  "level": "STABLE",
  "confidence": 0.0,
  "factors": [],
  "timeline": [],
  "alert": {},
  "sources": {},
  "created_at": "ISO-8601 timestamp"
}
```

### Index levels

```text
0–29   STABLE
30–59  WATCH
60–79  STRESSED
80–100 CRITICAL
```

### Alert states

```text
NO_ALERT
ALERT_DISPATCHED
ALERT_BLOCKED_STALE
```

## 4. GET /health

Checks whether the backend is running.

### Response

```json
{
  "status": "ok"
}
```

## 5. POST /api/analyze

Runs an analysis for a selected region.

### Request

```json
{
  "region_id": "gulf-of-mannar",
  "latitude": 9.0,
  "longitude": 79.0,
  "threshold": 70
}
```

### Response

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
  "factors": [
    {
      "name": "Sea Surface Temperature Anomaly",
      "category": "ocean",
      "impact": 31,
      "severity": "high",
      "description": "Elevated temperature signal detected."
    },
    {
      "name": "CPUE Decline",
      "category": "fisheries",
      "impact": 22,
      "severity": "medium",
      "description": "Catch-per-unit-effort shows a declining trend."
    },
    {
      "name": "Reduced Species Richness",
      "category": "molecular",
      "impact": 19,
      "severity": "high",
      "description": "eDNA results indicate reduced observed richness."
    }
  ],
  "timeline": [
    {
      "timestamp": "2026-08-12T10:00:00Z",
      "index": 28,
      "event": "Baseline"
    },
    {
      "timestamp": "2026-08-13T10:00:00Z",
      "index": 55,
      "event": "Environmental stress increased"
    },
    {
      "timestamp": "2026-08-14T10:00:00Z",
      "index": 88,
      "event": "Critical threshold crossed"
    }
  ],
  "alert": {
    "status": "ALERT_DISPATCHED",
    "threshold": 70,
    "reason": "Ecosystem index exceeded configured alert threshold."
  },
  "sources": {
    "ocean": "DEMO",
    "fisheries": "DEMO",
    "molecular": "DEMO"
  },
  "created_at": "2026-08-15T12:00:00Z"
}
```

## 6. POST /api/demo/analyze

Runs one of the predefined hackathon scenarios.

### Request

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

### Expected results

| Scenario | Index | Level | Alert |
|---|---:|---|---|
| `healthy_reef` | 22 | STABLE | NO_ALERT |
| `declining_fishery` | 55 | WATCH | NO_ALERT |
| `coral_bleaching` | 88 | CRITICAL | ALERT_DISPATCHED |

The primary demo may show the progression:

```text
28 → 88
```

as stress signals accumulate.

## 7. GET /api/region/{id}

Returns region information.

### Example

```text
GET /api/region/gulf-of-mannar
```

### Response

```json
{
  "id": "gulf-of-mannar",
  "name": "Gulf of Mannar",
  "latitude": 9.0,
  "longitude": 79.0,
  "bounding_box": {
    "min_lat": 8.5,
    "max_lat": 9.5,
    "min_lon": 78.5,
    "max_lon": 79.5
  },
  "source": "DEMO"
}
```

## 8. GET /api/insight/{id}

Returns a previously generated analysis.

### Example

```text
GET /api/insight/analysis-001
```

### Response

Same structure as:

```text
POST /api/analyze
```

## 9. GET /api/timeline/{id}

Returns ecosystem-index history.

### Response

```json
{
  "analysis_id": "analysis-001",
  "timeline": [
    {
      "timestamp": "2026-08-12T10:00:00Z",
      "index": 28,
      "event": "Baseline"
    },
    {
      "timestamp": "2026-08-13T10:00:00Z",
      "index": 55,
      "event": "Environmental stress increased"
    },
    {
      "timestamp": "2026-08-14T10:00:00Z",
      "index": 88,
      "event": "Critical threshold crossed"
    }
  ],
  "source": "DEMO"
}
```

## 10. GET /api/species/{id}

Returns species information associated with a region.

### Response

```json
{
  "region_id": "gulf-of-mannar",
  "species": [
    {
      "taxon": "Example species",
      "match_confidence": 0.94,
      "status": "common",
      "source": "DEMO"
    },
    {
      "taxon": "Example rare taxon",
      "match_confidence": 0.87,
      "status": "rare",
      "source": "DEMO"
    }
  ]
}
```

Allowed status values:

```text
common
rare
invasive
```

## 11. GET /api/edna/matches/{sample_id}

Returns eDNA/metabarcoding matches.

### Response

```json
{
  "sample_id": "sample-001",
  "species_richness": 17,
  "matches": [
    {
      "taxon": "Example species",
      "confidence": 0.96,
      "status": "common"
    },
    {
      "taxon": "Example rare taxon",
      "confidence": 0.82,
      "status": "rare"
    }
  ],
  "flags": [],
  "source": "DEMO"
}
```

Never return an eDNA match as scientifically certain.

Always provide a confidence score.

## 12. Alert Gate

The Alert Gate uses the ecosystem index and configured threshold.

### Rule

```text
index < threshold
→ NO_ALERT
```

```text
index >= threshold
→ ALERT_DISPATCHED
```

Example:

```text
45 + threshold 70
→ NO_ALERT
```

```text
87 + threshold 70
→ ALERT_DISPATCHED
```

### Stale data

```text
stale analysis
→ ALERT_BLOCKED_STALE
```

Response:

```json
{
  "status": "ALERT_BLOCKED_STALE",
  "threshold": 70,
  "reason": "Analysis data is stale."
}
```

## 13. Data Source Status

Every data-derived response must identify its source.

Allowed values:

```text
LIVE
CACHED
HISTORICAL
DEMO
```

Example:

```json
{
  "sources": {
    "ocean": "DEMO",
    "fisheries": "HISTORICAL",
    "molecular": "DEMO"
  }
}
```

Do not claim data is `LIVE` unless it actually came from a live source.

## 14. Error Response

All API errors should follow:

```json
{
  "error": {
    "code": "INVALID_REGION",
    "message": "The supplied region could not be found."
  }
}
```

Common error codes:

```text
INVALID_REGION
INVALID_COORDINATES
INVALID_SAMPLE
INVALID_SCENARIO
STALE_ANALYSIS
DATA_UNAVAILABLE
INTERNAL_ERROR
```

## 15. Frontend Integration Rule

Frontend developers should initially use:

```text
POST /api/demo/analyze
```

Do not hard-code separate UI logic for every scenario.

The UI should render whatever the backend returns.

Flow:

```text
User selects scenario
        ↓
POST /api/demo/analyze
        ↓
Backend
        ↓
Fusion Engine
        ↓
Alert Gate
        ↓
JSON response
        ↓
Frontend renders result
```

## 16. Backend ↔ Fusion Engine Rule

The Fusion Engine must return:

```text
index
level
confidence
factors
timeline
sources
```

The Backend is responsible for:

```text
API validation
request handling
response formatting
Alert Gate
error handling
```

The Fusion Engine is responsible for:

```text
feature processing
scoring
index calculation
confidence
explainability
```

## 17. 24-Hour Hackathon Priority

Implement in this order:

```text
1. /health
2. /api/demo/analyze
3. Fusion Engine
4. Alert Gate
5. Frontend dashboard
6. Timeline
7. Map
8. eDNA demo
9. Real data APIs
10. Advanced ML
```

The system must remain functional without external APIs.

Fallback:

```text
LIVE
 ↓
CACHED
 ↓
HISTORICAL
 ↓
DEMO
```

## 18. Contract Change Rule

Do not change:

- endpoint names
- field names
- enum values
- response structure

without informing all four team members.

If a change is necessary:

```text
1. Announce change in team channel.
2. Update this file.
3. Update backend.
4. Update frontend.
5. Test the complete flow.
6. Commit both changes together.
```

## Final Integration Test

The project is integrated correctly when this works:

```text
SELECT CORAL BLEACHING
        ↓
POST /api/demo/analyze
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

No team member should need to manually modify frontend data to make this demo work.
