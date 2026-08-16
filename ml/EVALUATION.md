# OceanPulse AI — `ml/` — Evaluation & Handoff Documentation

**Task 6 deliverable.** Per `implementation_plan.md` Phase 5 / Phase 11
and the Task 6 card: *"Document exactly what was implemented and what
was actually measured."* This file is that document. It does not
repeat everything in `README.md` — it points there for design detail
and focuses on what a new team member (or the Backend integrator)
needs to run, test, and trust this layer.

---

## 1. What was implemented (Tasks 1–5 summary)

| # | Deliverable | Location | Status |
|---|---|---|---|
| 1 | Rule-based Insight Fusion Engine (index/level/confidence/factors/timeline) | `fusion_engine/` | Implemented, zero ML dependencies |
| 2 | Index classification bands (0–29/30–59/60–79/80–100) | `fusion_engine/fusion.py: index_to_level()` | Implemented |
| 3 | Explainability (factors + timeline) | `fusion_engine/scoring.py`, `fusion.py` | Implemented |
| 4 | Three deterministic demo scenarios | `fusion_engine/demo_scenarios.py` | Implemented |
| 5 | ML input/output schema | `models/schema.py`, `models/converters.py` | Implemented |
| 6 | XGBoost fisheries/CPUE interface | `models/xgboost_fisheries.py` | Implemented (heuristic fallback tier active — no trained artifact) |
| 7 | IsolationForest ecosystem-anomaly interface | `models/isolation_forest_anomaly.py` | Implemented (heuristic fallback tier active — no trained artifact) |
| 8 | ML-enhanced Fusion Engine (optional wrapper) | `models/ml_fusion_engine.py` | Implemented |
| 9 | Regression/integration test suite | `tests/test_regression_integration.py` | Implemented, passing |
| 10 | Evaluation script | `evaluate.py` (this task) | Implemented |

**No model has been trained in this MVP.** Both `XGBoostFisheriesInterface`
and `IsolationForestAnomalyInterface` are real, working interfaces that
would load a trained artifact automatically if one existed — but none
does, because training either model requires labeled fisheries-outcome
or labeled-anomaly data this hackathon does not have. This is by design
per `CLAUDE.md`'s ML fallback chain (trained model → heuristic → rule-based
→ demo), and is reported honestly rather than simulated.

---

## 2. What was actually measured

Run `python evaluate.py` from `ml/` to reproduce every number in this
section — nothing below is hand-typed without also being produced by
that script.

### 2.1 Model availability (measured, live)

```
xgboost_fisheries:         available=False   model_version=None
isolation_forest_anomaly:  available=False   model_version=None
```

Both models are currently running in their **heuristic-fallback tier**
(deterministic rule-based scoring — see `xgboost_fisheries.py` and
`isolation_forest_anomaly.py` docstrings for the exact thresholds).
This is tier 3 of `CLAUDE.md`'s four-tier ML fallback chain, not tier 1.

### 2.2 Precision / Recall / F1 / ROC-AUC / false-positive rate

**Not measured. Not reported. Deliberately.**

These metrics require a labeled evaluation dataset (real inputs paired
with a known-correct outcome) that does not exist in this repository.
`evaluate.py` looks for one at:

- `ml/eval_data/fisheries_eval.csv`
- `ml/eval_data/anomaly_eval.csv`

Neither file is present, and none is fabricated to fill this section.
Per `CLAUDE.md`: *"Report Precision, Recall, F1, ROC-AUC, and
false-positive rate only when measured"* and *"Never fabricate ...
model metrics."* If you add a labeled dataset in the documented CSV
format (column headers are specified in `evaluate.py`'s module
docstring) and re-run the script, it will compute and print real
numbers for whichever tier is active (heuristic fallback today, the
trained model automatically once one is loaded) and write them to
`ml/eval_report.json`. Until then, this section stays empty rather
than guessed.

### 2.3 Determinism, boundaries, demo scenarios, explainability, regression

These ARE measured — by the test suite and verification scripts, not
by this evaluation script (they test the Fusion Engine's correctness,
not a trained model's accuracy). Reproduce with:

```bash
cd ml
python -m pytest tests/ -v                # 97 tests, all passing
python verify_determinism.py               # same input -> same output
python verify_boundaries.py                # 29/30/59/60/79/80 boundary values
python verify_explainability.py            # non-empty factors + timeline
python verify_demo_scenarios.py            # 22/55/88, 5 runs each, 15 total
python verify_ml_integration.py            # ML-enabled/disabled combination logic
python verify_regression_integration.py    # full regression suite incl. malformed input
```

Last known-good result of the full suite (reproduced by running the
commands above in this environment):

```
97 passed in 0.23s
```

All six verification scripts exit 0. See each script's own console
output for the specific values checked (index boundaries, scenario
index/level pairs, factor/timeline contents) — they are not
reproduced here to avoid two sources of truth drifting apart; run the
scripts.

---

## 3. Model / version information

| Model | Trained artifact expected at | Present? | `model_version` when loaded | Currently reports |
|---|---|---|---|---|
| XGBoost fisheries/CPUE classifier | `models/artifacts/xgboost_fisheries_model.json` | No | basename of the artifact file | `available=False`, `model_version=None` |
| IsolationForest ecosystem anomaly | `models/artifacts/isolation_forest_ecosystem_model.joblib` | No | basename of the artifact file | `available=False`, `model_version=None` |

Neither `models/artifacts/` path is created or committed by this task
— its absence is what keeps the heuristic-fallback tier active, and
that absence is itself the correct, honest state for this MVP.

If a real trained artifact is later placed at either path (and the
matching optional dependency — `xgboost` or `joblib`/`scikit-learn` —
is installed), `XGBoostFisheriesInterface` / `IsolationForestAnomalyInterface`
pick it up automatically on next construction. No code changes are
needed anywhere in `fusion_engine/`, `models/ml_fusion_engine.py`, or
the Backend integration layer for this to activate.

---

## 4. Input schema

### 4.1 Fusion Engine input (`fusion_engine/schema.py`)

`FusionInput(region_id, ocean, fisheries, molecular, history=[])` —
`ocean` / `fisheries` / `molecular` are each optional; the engine
degrades gracefully (lower confidence) rather than failing when one is
missing. Field-level detail is in `README.md` — this file only covers
the ML-specific schema layered on top.

### 4.2 XGBoost fisheries model input (`models/schema.py: XGBOOST_FEATURE_SPECS`)

| Feature | Type | Range | Source |
|---|---|---|---|
| `cpue_trend_pct` | float | -100.0 to 100.0 | `FisheriesFeatures.cpue_trend_pct` |
| `vessel_density_index` | float | 0.0 to 1.0 | `FisheriesFeatures.vessel_density_index` |

### 4.3 IsolationForest anomaly model input (`models/schema.py: ISOLATION_FOREST_FEATURE_SPECS`)

| Feature | Type | Range | Source |
|---|---|---|---|
| `sst_anomaly_c` | float | -5.0 to 10.0 | `OceanFeatures.sst_anomaly_c` |
| `chlorophyll_a_anomaly_pct` | float | -100.0 to 500.0 | `OceanFeatures.chlorophyll_a_anomaly_pct` |
| `salinity_anomaly_psu` | float | -10.0 to 10.0 | `OceanFeatures.salinity_anomaly_psu` |
| `cpue_trend_pct` | float | -100.0 to 100.0 | `FisheriesFeatures.cpue_trend_pct` |
| `vessel_density_index` | float | 0.0 to 1.0 | `FisheriesFeatures.vessel_density_index` |
| `species_richness_delta_pct` | float | -100.0 to 100.0 | derived: `(baseline_richness - species_richness) / baseline_richness * 100` |

Both tables are the literal source of truth in `models/schema.py` —
if the two ever disagree, the code wins; update this file to match.

Invalid input (missing/None, non-numeric, or out of the documented
range) raises `models.converters.FeatureValidationError` — a typed,
catchable exception, not an opaque crash. `XGBoostFisheriesInterface.predict()`
propagates this; `IsolationForestAnomalyInterface.predict()` catches it
internally and returns a safe `available=False` output instead (see
its docstring for why the two interfaces differ here).

---

## 5. Output schema

### 5.1 `XGBoostOutput` (`models/schema.py`)

| Field | Type | Meaning |
|---|---|---|
| `stock_trend_class` | `StockTrendClass \| None` | `stable` / `declining` / `critical_decline` |
| `confidence` | `float \| None` (0.0–1.0) | Model probability when `available=True`; a "how clear-cut" heuristic score (NOT a probability) when running the fallback tier |
| `model_version` | `str \| None` | Trained-artifact filename, or `None` in fallback mode |
| `available` | `bool` | `True` only when real trained-model inference actually ran |

### 5.2 `IsolationForestOutput` (`models/schema.py`)

| Field | Type | Meaning |
|---|---|---|
| `normalized_anomaly_score` | `float \| None` (0.0–1.0) | Higher = more anomalous (sklearn's sign convention already flipped for callers) |
| `is_anomaly` | `bool \| None` | Score ≥ threshold (fallback tier: 0.35) or sklearn's own `-1` prediction (trained tier) |
| `model_version` | `str \| None` | Trained-artifact filename, or `None` in fallback mode |
| `available` | `bool` | `True` only when real trained-model inference actually ran |

### 5.3 `MLFusionResult` (`models/ml_fusion_engine.py`)

A superset of `fusion_engine.schema.FusionResult` (same
`index`/`level`/`confidence`/`factors`/`timeline`/`sources` fields,
same types — this is what `API_CONTRACT.md` section 3 defines) plus
two internal-only fields:

| Extra field | Type | Meaning |
|---|---|---|
| `ml_enhanced` | `bool` | Whether any trained model actually contributed to this result |
| `model_status` | `dict` | Per-model `{available, model_version}`, for debugging/observability |

**`ml_enhanced` and `model_status` are NOT part of `API_CONTRACT.md`**
and must not be added to the HTTP response without going through
section 18's contract-change process. A Backend that reads only the
six contract fields can treat `MLFusionResult` as a plain `FusionResult`
and ignore both.

---

## 6. Fallback behavior

```
Live oceanographic/fisheries/molecular data
        ↓ (Data layer, not this module)
Normalized FusionInput (ocean / fisheries / molecular, each optional)
        ↓
ML Input Schema (models/converters.py) — validates + converts
        ↓
   ┌─────────────────────────┬─────────────────────────────┐
   │ XGBoost fisheries       │ IsolationForest anomaly      │
   │ (models/xgboost_        │ (models/isolation_forest_    │
   │  fisheries.py)          │  anomaly.py)                 │
   └─────────────────────────┴─────────────────────────────┘
        ↓ each model, independently:
        ↓   trained artifact loaded?  -> real inference, available=True
        ↓   otherwise                 -> heuristic fallback, available=False
        ↓
MLEnhancedFusionEngine (models/ml_fusion_engine.py)
   - runs fusion_engine.FusionEngine (rule-based) FIRST, always
   - adds a Factor per model that is actually available=True
   - if NEITHER model is available: returns the rule-based result
     unchanged (ml_enhanced=False) — this is today's state
        ↓
Index / Explainability (factors, timeline, confidence, sources)
        ↓
Backend (owns API validation, response formatting, Alert Gate)
        ↓
Alert Gate: index >= threshold -> ALERT_DISPATCHED, else NO_ALERT
            stale analysis     -> ALERT_BLOCKED_STALE
```

This matches the "Required Architecture" diagram from the Task 6
handoff brief exactly:
`Normalized Data → ML Input Schema → XGBoost + IsolationForest →
Fusion Engine → Index / Explainability → Backend → Alert Gate`,
with fallback `ML available → use ML outputs. ML unavailable →
rule-based scoring → demo scenario.`

Every layer in this chain fails **safely, not silently-wrong**:
- Bad/out-of-range ML input → `FeatureValidationError` (typed, caught
  at the `MLEnhancedFusionEngine` boundary, never crashes `analyze()`).
- No trained model → heuristic tier, clearly labeled `available=False`.
- No signal category at all (e.g. no eDNA sample) → the rule-based
  engine still returns a result, with reduced confidence.
- Demo scenarios never depend on any of the above — they are
  calibrated feature inputs run through the exact same pipeline,
  confirmed identical across five repeated runs each (§2.3).

---

## 7. Exact commands

```bash
cd ml

# Install (only needed once a trained model + eval dataset exist —
# Task 1-6 as shipped needs no third-party packages, since the
# fallback tiers are pure standard library)
pip install -r requirements.txt

# Full test suite
python -m pytest tests/ -v

# Individual sign-off scripts (Fusion Engine)
python verify_determinism.py
python verify_boundaries.py
python verify_explainability.py
python verify_demo_scenarios.py

# Individual sign-off scripts (ML integration)
python verify_ml_integration.py
python verify_regression_integration.py

# Evaluation (Task 6) — reports live model status + heuristic-tier
# behavior always; computes real Precision/Recall/F1/ROC-AUC/FPR only
# if ml/eval_data/*.csv exists (see evaluate.py docstring for format)
python evaluate.py

# Inference (interactive, from a Python shell in ml/)
python -c "
from fusion_engine.demo_scenarios import get_scenario
from models.ml_fusion_engine import MLEnhancedFusionEngine

engine = MLEnhancedFusionEngine()
result = engine.analyze(get_scenario('coral_bleaching'))
print(result.index, result.level, result.confidence, result.ml_enhanced)
"
```

---

## 8. Handoff to Backend

- **ML interface path:** `ml/models/ml_fusion_engine.py`
- **Callable:** `MLEnhancedFusionEngine().analyze(fusion_input)` →
  `MLFusionResult`, or the module-level convenience function
  `models.ml_fusion_engine.analyze_with_ml(fusion_input)`.
  (`fusion_engine.FusionEngine().analyze(fusion_input)` also works
  standalone if the Backend wants zero ML dependency in its critical
  path — both take the identical `FusionInput` and return
  contract-compatible output.)
- **Input schema:** `fusion_engine.schema.FusionInput` — see §4.1 and
  `README.md`. The Backend builds this from ingested/normalized data;
  nothing in `ml/` fetches or normalizes raw data itself.
- **Output schema:** `MLFusionResult` — a superset of the
  `API_CONTRACT.md` §3 response shape (`index`, `level`, `confidence`,
  `factors`, `timeline`, `sources`). Read only those six fields when
  populating the HTTP response; `ml_enhanced` / `model_status` are for
  internal use only (§5.3).
- **Model availability behavior:** call `MLEnhancedFusionEngine().model_status()`
  independently of `analyze()` for a startup/health check — it costs
  one `os.path.exists()` per model and needs no feature data. See §2.1
  for today's actual (both unavailable) status.
- **Model version:** `None` for both models today (§3) — report this
  honestly if the Backend surfaces it anywhere (e.g. an internal debug
  panel); do not display a placeholder version string.
- **Exact test command:** `cd ml && python -m pytest tests/ -v` (97
  tests) plus `python verify_regression_integration.py` for the
  end-to-end regression/alert-flow check the Backend integrator should
  run after wiring this in.
- **What Backend must still own** (unchanged from `README.md` / `API_CONTRACT.md`
  §16): API validation, request handling, response formatting, the
  Alert Gate (`NO_ALERT` / `ALERT_DISPATCHED` / `ALERT_BLOCKED_STALE`),
  and all error handling. Nothing in `ml/` makes an alert decision or
  talks to the network/database.

---

## 9. Contracts this task did not touch

Per the Task 6 brief's "Do Not Break These Existing Contracts" — all
verified still true by the commands in §7, not just asserted here:

- API endpoint names and response field names — unchanged; `ml/` has
  no HTTP layer and never did.
- The 0–100 ecosystem index and its four classification bands —
  unchanged; `MLEnhancedFusionEngine` reuses `fusion_engine.fusion.index_to_level()`
  verbatim, no new bands defined.
- The three deterministic demo scenarios (22/STABLE, 55/WATCH,
  88/CRITICAL) — unchanged; confirmed byte-for-byte identical through
  `MLEnhancedFusionEngine` in today's ML-unavailable state (§2.3).
- `DEMO`/`LIVE`/`CACHED`/`HISTORICAL` source labeling — unchanged;
  `sources` is passed through from the rule-based result untouched.
- The Backend Alert Gate and stale-data behavior — untouched; `ml/`
  does not implement or call an Alert Gate (§8).
- The rule-based fallback that keeps the demo functional without ML —
  unchanged and still the default path today, since no trained model
  artifacts exist.

---

## 10. Final completion checklist

- [x] ML input schema implemented — `models/schema.py`, `models/converters.py`
- [x] XGBoost fisheries interface implemented — `models/xgboost_fisheries.py`
- [x] IsolationForest anomaly interface implemented — `models/isolation_forest_anomaly.py`
- [x] ML outputs connected to Fusion Engine — `models/ml_fusion_engine.py`
- [x] Rule-based fallback preserved — `fusion_engine/fusion.py` untouched; `verify_ml_integration.py` check [2]
- [x] Existing 22/55/88 scenarios still pass — `verify_demo_scenarios.py`, `verify_regression_integration.py` [2]
- [x] Boundary tests pass — `verify_boundaries.py`, `verify_regression_integration.py` [1]
- [x] ML-disabled mode passes — `verify_ml_integration.py` [2], `verify_regression_integration.py` [3]
- [x] No fabricated metrics or live-data claims — enforced structurally by `evaluate.py` (§2.2); every `source` field is `DEMO`, never `LIVE`
- [x] README/documentation updated — this file, plus `README.md`'s existing Task 1–5 sections

All ten items are backed by a command in §7 that reproduces the
result — none is a claim without a corresponding check.
