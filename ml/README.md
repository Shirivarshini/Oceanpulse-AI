# OceanPulse AI — `ml/` — Insight Fusion Engine

**Task 1 deliverable.** Deterministic, rule-based core described in
`CLAUDE.md` priority #1 and `implementation_plan.md` Phase 4.

Contains the Fusion Engine, scoring, classification, confidence, and explainability.

## What this is

A pure Python module that turns normalized ocean / fisheries / molecular
(eDNA) features into a single explainable **0–100 ecosystem index**, an
index **level** (`STABLE` / `WATCH` / `STRESSED` / `CRITICAL`), a
**confidence** score, a list of contributing **factors**, and a
**timeline**. Field names match `API_CONTRACT.md` section 3 exactly so
the Backend (Task 2/3) can pass this straight into the response model.

No network calls. No database. No ML models yet (that's Phase 5). No
randomness anywhere. Same input always produces the same output.

## Files

```
ml/
├── fusion_engine/
│   ├── __init__.py             # public exports
│   ├── schema.py               # FusionInput / FusionResult dataclasses
│   ├── scoring.py              # rule-based per-category factor extraction
│   ├── fusion.py               # FusionEngine — combines factors into the index + level + confidence
│   └── demo_scenarios.py       # calibrated inputs for the 3 hackathon demos
├── tests/
│   ├── test_fusion_engine.py          # unit tests incl. determinism check
│   ├── test_index_classification.py   # boundary + confidence tests
│   ├── test_explainability.py         # factor + timeline tests
│   └── test_demo_scenarios.py         # five-consecutive-runs tests
├── verify_determinism.py              # verification script
├── verify_boundaries.py               # verification script
├── verify_explainability.py           # verification script
├── verify_demo_scenarios.py           # verification script
├── requirements.txt
└── README.md
```

## Quickstart

```bash
cd ml
python -m pytest tests/ -v          # full test suite (34 tests)
python verify_determinism.py        # sign-off check
python verify_boundaries.py         # sign-off check
python verify_explainability.py     # sign-off check
python verify_demo_scenarios.py     # sign-off check
```

No dependencies to install for Task 1 — everything here is standard
library. `requirements.txt` only lists what Phase 5 (ML Integration)
will eventually need.

## How the index is built

```
OceanFeatures ──┐
FisheriesFeatures ─┼─► scoring.score_*() ─► [Factor, Factor, ...] ─► sum, clamp 0-100 ─► index
MolecularFeatures ─┘                                                                    │
                                                                                          ▼
                                                                                     index_to_level()
```

Category impact budgets (sum to 100):

| Category  | Primary factor              | Cap | Secondary factor         | Cap |
|-----------|------------------------------|-----|---------------------------|-----|
| ocean     | Sea Surface Temperature Anomaly | 32  | Harmful Algal Bloom Indicator | 8   |
| fisheries | CPUE Decline                 | 27  | Vessel Density Spike       | 8   |
| molecular | Reduced Species Richness      | 18  | Invasive/Rare Taxon Detected | 7   |

Thresholds and scaling are documented inline in `scoring.py`. All rules
are linear and simple by design — this is the MVP "rule-based scoring"
tier of `CLAUDE.md`'s ML fallback chain:

```
1. Trained classifier/matcher   (Phase 5)
2. Similarity/heuristic match
3. Rule-based scoring            <-- this module
4. Demo scenario                 <-- demo_scenarios.py
```

## Confidence

Confidence reflects **data completeness and quality**, not the size of
the index — a confidently `STABLE` region should read as confident, not
uncertain. It starts from how many of the three signal categories are
present, then applies a small penalty if eDNA `sample_quality` is low.
Per `CLAUDE.md`: *"Explicitly flag low-confidence or sparse-data regions
in the UI rather than hiding the gap."*

## Demo scenarios

`demo_scenarios.py` holds calibrated (not hardcoded-output) feature
inputs for the three required hackathon scenarios. Running them through
the same scoring pipeline used for live regions reproduces the exact
values from `API_CONTRACT.md` section 6:

| Scenario            | Index | Level    |
|----------------------|------:|----------|
| `healthy_reef`        | 22    | STABLE   |
| `declining_fishery`   | 55    | WATCH    |
| `coral_bleaching`     | 88    | CRITICAL |

`coral_bleaching` also carries a pre-baked `history` so its timeline
replays the `28 → 55 → 88` escalation from the contract, not just the
final number.

## Index classification (Task 2)

`index_to_level()` in `fusion.py` maps the 0-100 index to a level using
the exact bands from `API_CONTRACT.md` section 3:

| Index range | Level    |
|-------------|----------|
| 0–29        | STABLE   |
| 30–59       | WATCH    |
| 60–79       | STRESSED |
| 80–100      | CRITICAL |

`tests/test_index_classification.py` and `verify_boundaries.py` check
all six required boundary values (29, 30, 59, 60, 79, 80) independently
of the rest of the engine, plus confidence-specific tests (full vs.
partial signal coverage, low eDNA sample quality, valid range).

## Explainability (Task 3)

Every analysis returns two things that explain the index, not just the
number itself:

- **`factors`** — from `scoring.py`, each with a `name`, `category`
  (`ocean` / `fisheries` / `molecular`), `impact` (points contributed to
  the index), `severity` (`low` / `medium` / `high`), and a
  plain-language `description` that avoids confirmed-conclusion language
  per `CLAUDE.md`.
- **`timeline`** — from `fusion.py`'s `_build_timeline()`, a list of
  timestamped events showing how the index arrived at its current value.
  Live/first-time analyses get a single "Baseline" point; `coral_bleaching`
  carries pre-baked history so it replays the full `28 → 55 → 88`
  escalation.

`tests/test_explainability.py` and `verify_explainability.py` confirm
every demo scenario returns non-empty `factors` and `timeline` arrays
with the correct field shapes.

## Demo scenario verification (Task 4)

`tests/test_demo_scenarios.py` and `verify_demo_scenarios.py` run each
of the three scenarios five times consecutively (15 runs total) and
confirm every run returns exactly the required index/level, that all
three signal categories (ocean/fisheries/molecular) are attached to
each scenario, and that both the input schema and the `FusionResult.sources`
output report every category as `DEMO`.

## What this module deliberately does NOT do

Per `API_CONTRACT.md` section 16 and `CLAUDE.md`:

- **No Alert Gate.** The engine returns an index; deciding
  `NO_ALERT` / `ALERT_DISPATCHED` / `ALERT_BLOCKED_STALE` against a
  threshold is the Backend's job (Task/Phase 8).
- **No API validation, request handling, or error formatting.** Backend's job.
- **No live data fetching.** Data-pipeline's job — this module only
  consumes already-normalized `OceanFeatures` / `FisheriesFeatures` /
  `MolecularFeatures`.

## Integration contract (for whoever wires this into FastAPI)

```python
from fusion_engine import FusionEngine, FusionInput, OceanFeatures, FisheriesFeatures, MolecularFeatures
from fusion_engine.demo_scenarios import get_scenario

engine = FusionEngine()

# Live/region path — Backend builds FusionInput from ingested + normalized data
result = engine.analyze(FusionInput(region_id="gulf-of-mannar", ocean=..., fisheries=..., molecular=...))

# Demo path — POST /api/demo/analyze
result = engine.analyze(get_scenario("coral_bleaching"))  # raises KeyError -> map to INVALID_SCENARIO

# result.index, result.level, result.confidence, result.factors, result.timeline, result.sources
# map 1:1 onto the API_CONTRACT.md response fields of the same names.
```
>>>>>>> 600b9a7 (ml module files added)
