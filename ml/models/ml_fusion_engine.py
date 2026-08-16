"""
OceanPulse AI — ML Models
Task 4: Integrate ML Outputs with the Fusion Engine.

Deliverable: optional ML-enhanced Fusion Engine.

This module is the ONLY place in `ml/` that imports both
`fusion_engine` (Task 1) and `models` (Tasks 1-3). That keeps the
dependency graph one-way and additive, exactly as README.md documents:

    fusion_engine/   -- zero ML dependencies, must keep working alone
    models/          -- depends on fusion_engine/schema only
    models/ml_fusion_engine.py (this file) -- depends on BOTH, and is
                        the sole integration point between them

`fusion_engine/fusion.py` is NOT modified by this task. The rule-based
`FusionEngine` remains the guaranteed, ML-free core described in
CLAUDE.md priority #1 — "the engine works without ML." This module
wraps it with composition (not inheritance, not monkeypatching) and
only ever ADDS to what the rule-based engine already produced.

How ML output is combined into the index (per the task card):
  - "Add model availability detection."
        -> `MLEnhancedFusionEngine.model_status()` and the
           `model_status` field on every `MLFusionResult`.
  - "Combine XGBoost and IsolationForest outputs with the existing
     rule-based signals."
        -> Each model that is actually AVAILABLE (a real trained
           model loaded — see xgboost_fisheries.py /
           isolation_forest_anomaly.py) contributes an additional
           `Factor` on top of the rule-based ones, using the same
           `fusion_engine.schema.Factor` shape the frontend already
           renders. Model output that is only running in its own
           heuristic-fallback tier (`available=False`, the current
           state — no trained artifacts exist yet) contributes
           NOTHING, by design (see "do not break existing demo
           scenarios" below).
  - "Preserve index classification: 0-29 STABLE, 30-59 WATCH,
     60-79 STRESSED, 80-100 CRITICAL."
        -> The combined index is re-clamped to 0-100 and passed
           through the SAME `fusion_engine.fusion.index_to_level()`
           used by the rule-based engine. No new bands are defined
           here.
  - "Preserve confidence, factors, timeline, and source metadata."
        -> `timeline` and `sources` are passed through from the base
           result untouched. `factors` extends (never replaces) the
           base list. `confidence` only ever increases (capped at the
           engine's existing 0.98 ceiling) to reflect the extra,
           independently-modeled evidence — it is never lowered by
           this layer.
  - "Keep rule-based scoring as fallback when ML is disabled."
        -> If neither model is available, `analyze()` returns the
           base `FusionResult` fields completely unchanged
           (`ml_enhanced=False`).
  - "Do not break existing demo scenarios."
        -> No trained model artifacts ship with this MVP (see
           `models/xgboost_fisheries.py` / `isolation_forest_anomaly.py`
           docstrings), so both interfaces report `available=False`
           today. That means `MLEnhancedFusionEngine` is currently a
           pure pass-through of `FusionEngine` for every scenario —
           verified by `tests/test_ml_fusion_engine.py::
           test_demo_scenarios_unchanged_when_no_trained_models` and
           `verify_ml_integration.py`. The moment a real model is
           placed at either `models/artifacts/...` path, this layer
           activates automatically with no code changes required
           anywhere else.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional

from fusion_engine.fusion import FusionEngine, index_to_level
from fusion_engine.schema import Factor, FusionInput, FusionResult

from .converters import FeatureValidationError
from .isolation_forest_anomaly import IsolationForestAnomalyInterface
from .schema import IsolationForestOutput, StockTrendClass, XGBoostOutput
from .xgboost_fisheries import XGBoostFisheriesInterface

# Confidence contribution per model that actually ran on a trained
# artifact (available=True). Additive, capped by FusionEngine's own
# 0.30-0.98 confidence range — this layer never pushes confidence
# outside bounds the rule-based engine already enforces.
_XGBOOST_CONFIDENCE_BOOST = 0.03
_ISOLATION_FOREST_CONFIDENCE_BOOST = 0.04
_CONFIDENCE_CEILING = 0.98

# Impact caps for ML-derived factors, expressed as extra points on top
# of the rule-based 0-100 budget (which already sums its own category
# caps to 100 — see fusion_engine/scoring.py). Kept intentionally small
# relative to the rule-based factors so a trained model REFINES the
# index rather than dominating it.
_XGBOOST_IMPACT_BY_CLASS = {
    StockTrendClass.STABLE: 0,
    StockTrendClass.DECLINING: 5,
    StockTrendClass.CRITICAL_DECLINE: 10,
}
_ISOLATION_FOREST_MAX_IMPACT = 12


@dataclass
class MLFusionResult(FusionResult):
    """
    `FusionResult` plus optional ML-integration metadata.

    Deliberately a SUPERSET of `FusionResult` (same field names, same
    types, same order) rather than a different shape — a Backend that
    only reads `index/level/confidence/factors/timeline/sources`
    (the fields defined in API_CONTRACT.md section 3) can consume this
    exactly like a plain `FusionResult` and simply ignore the two new
    fields. The two new fields are NOT part of API_CONTRACT.md and
    must not be added to the HTTP response without following section
    18's contract-change process.
    """
    ml_enhanced: bool = False
    model_status: Dict[str, dict] = field(default_factory=dict)


class MLEnhancedFusionEngine:
    """
    Wraps the rule-based `FusionEngine` and adds ML-derived factors
    from the XGBoost fisheries and IsolationForest ecosystem-anomaly
    interfaces when — and only when — a real trained model is loaded.

    Stateless across calls other than the (cheap, one-time) model-load
    attempt each wrapped interface performs at construction. Dependency
    injection via the constructor lets tests exercise the "ML
    available" branch without needing an actual trained model artifact
    on disk.
    """

    def __init__(
        self,
        base_engine: Optional[FusionEngine] = None,
        xgboost_interface: Optional[XGBoostFisheriesInterface] = None,
        isolation_forest_interface: Optional[IsolationForestAnomalyInterface] = None,
    ):
        self.base_engine = base_engine or FusionEngine()
        self.xgboost_interface = xgboost_interface or XGBoostFisheriesInterface()
        self.isolation_forest_interface = (
            isolation_forest_interface or IsolationForestAnomalyInterface()
        )

    # -- public API ----------------------------------------------------

    def model_status(self) -> Dict[str, dict]:
        """
        Model availability detection, independent of any single
        analysis run. Safe to call before `analyze()` (e.g. for a
        startup/health check) since it only reflects whether each
        wrapped interface successfully loaded a trained model file —
        it does not require feature data.
        """
        return {
            "xgboost_fisheries": {
                "available": self.xgboost_interface.is_available(),
                "model_version": self.xgboost_interface.model_version,
            },
            "isolation_forest_anomaly": {
                "available": self.isolation_forest_interface.is_available(),
                "model_version": self.isolation_forest_interface.model_version,
            },
        }

    def analyze(self, fusion_input: FusionInput) -> MLFusionResult:
        """
        Run the rule-based Fusion Engine first — this is the
        guaranteed result and the fallback CLAUDE.md requires. Then,
        for each ML model that is actually available, fold its output
        in as additional explainable factors and a small confidence
        boost. When no model is available, return the rule-based
        result completely unchanged (`ml_enhanced=False`).
        """
        base_result = self.base_engine.analyze(fusion_input)

        ml_factors = []
        confidence_boost = 0.0
        status: Dict[str, dict] = {}

        xgb_status, xgb_factor, xgb_boost = self._run_xgboost(fusion_input)
        status["xgboost_fisheries"] = xgb_status
        if xgb_factor is not None:
            ml_factors.append(xgb_factor)
        confidence_boost += xgb_boost

        iso_status, iso_factor, iso_boost = self._run_isolation_forest(fusion_input)
        status["isolation_forest_anomaly"] = iso_status
        if iso_factor is not None:
            ml_factors.append(iso_factor)
        confidence_boost += iso_boost

        if not ml_factors and confidence_boost == 0.0:
            # Fallback path — no trained model contributed anything.
            # Pass the rule-based result through completely unchanged
            # so demo scenarios and any other caller see identical
            # index/level/confidence/factors/timeline/sources to
            # plain FusionEngine.analyze().
            return MLFusionResult(
                index=base_result.index,
                level=base_result.level,
                confidence=base_result.confidence,
                factors=base_result.factors,
                timeline=base_result.timeline,
                sources=base_result.sources,
                ml_enhanced=False,
                model_status=status,
            )

        combined_factors = list(base_result.factors) + [
            f.__dict__ for f in ml_factors
        ]
        combined_factors.sort(key=lambda f: f["impact"], reverse=True)

        raw_index = base_result.index + sum(f.impact for f in ml_factors)
        index = max(0, min(100, round(raw_index)))
        level = index_to_level(index)

        confidence = round(
            min(_CONFIDENCE_CEILING, base_result.confidence + confidence_boost), 2
        )

        return MLFusionResult(
            index=index,
            level=level,
            confidence=confidence,
            factors=combined_factors,
            timeline=base_result.timeline,
            sources=base_result.sources,
            ml_enhanced=True,
            model_status=status,
        )

    # -- internals -------------------------------------------------

    def _run_xgboost(self, fusion_input: FusionInput):
        """
        Returns (status_dict, Factor|None, confidence_boost).

        No fisheries signal at all -> not applicable, no error.
        Fisheries signal present but invalid (out of range/non-numeric)
        -> reported in status, no factor, no boost, no exception raised
        to the caller (mirrors IsolationForest's "never breaks the
        pipeline" behavior for this integration layer, even though the
        underlying XGBoostFisheriesInterface.predict() itself does
        raise FeatureValidationError — this wrapper is the boundary
        that guarantees `analyze()` never crashes on bad ML input).
        """
        if fusion_input.fisheries is None:
            return (
                {"available": False, "model_version": None, "reason": "no_fisheries_signal"},
                None,
                0.0,
            )

        try:
            output: XGBoostOutput = self.xgboost_interface.predict(fusion_input.fisheries)
        except FeatureValidationError as exc:
            return (
                {"available": False, "model_version": None, "reason": f"invalid_input: {exc}"},
                None,
                0.0,
            )

        status = {"available": output.available, "model_version": output.model_version}
        if not output.available:
            return status, None, 0.0

        impact = _XGBOOST_IMPACT_BY_CLASS.get(output.stock_trend_class, 0)
        if impact <= 0:
            # Model confirms a stable stock trend — no additional index
            # pressure, but the model DID run, so it still earns its
            # confidence boost (handled by the caller via confidence_boost).
            return status, None, _XGBOOST_CONFIDENCE_BOOST

        conf_pct = (
            f" (model confidence {output.confidence:.0%})"
            if output.confidence is not None else ""
        )
        factor = Factor(
            name="ML Fisheries Stock Classification",
            category="fisheries",
            impact=impact,
            severity="high" if output.stock_trend_class == StockTrendClass.CRITICAL_DECLINE else "medium",
            description=(
                f"XGBoost fisheries stock classifier (model "
                f"{output.model_version}) indicates a pattern consistent "
                f"with {output.stock_trend_class.value.replace('_', ' ')} "
                f"stock status{conf_pct}."
            ),
        )
        return status, factor, _XGBOOST_CONFIDENCE_BOOST

    def _run_isolation_forest(self, fusion_input: FusionInput):
        """
        Returns (status_dict, Factor|None, confidence_boost).

        `IsolationForestAnomalyInterface.predict()` never raises (see
        its own docstring — unavailable model/invalid input both
        resolve to `available=False`), so no try/except is needed here.
        """
        if (
            fusion_input.ocean is None
            and fusion_input.fisheries is None
            and fusion_input.molecular is None
        ):
            return (
                {"available": False, "model_version": None, "reason": "no_signals"},
                None,
                0.0,
            )

        output: IsolationForestOutput = self.isolation_forest_interface.predict(
            fusion_input.ocean, fusion_input.fisheries, fusion_input.molecular
        )

        status = {"available": output.available, "model_version": output.model_version}
        if not output.available:
            return status, None, 0.0

        if not output.is_anomaly:
            # Model ran and found nothing unusual -- still earns its
            # confidence boost, no index change.
            return status, None, _ISOLATION_FOREST_CONFIDENCE_BOOST

        impact = round(min(
            _ISOLATION_FOREST_MAX_IMPACT,
            output.normalized_anomaly_score * _ISOLATION_FOREST_MAX_IMPACT,
        ))
        if impact <= 0:
            return status, None, _ISOLATION_FOREST_CONFIDENCE_BOOST

        factor = Factor(
            name="ML Ecosystem Anomaly Detected",
            category="ecosystem",
            impact=impact,
            severity="high" if output.normalized_anomaly_score >= 0.66 else "medium",
            description=(
                f"IsolationForest ecosystem anomaly model (model "
                f"{output.model_version}, score "
                f"{output.normalized_anomaly_score:.2f}) flags this "
                "region's combined ocean/fisheries/molecular signal "
                "pattern as anomalous relative to typical conditions."
            ),
        )
        return status, factor, _ISOLATION_FOREST_CONFIDENCE_BOOST


def analyze_with_ml(
    fusion_input: FusionInput,
    engine: Optional[MLEnhancedFusionEngine] = None,
) -> MLFusionResult:
    """Module-level convenience wrapper, mirroring the other models/ modules."""
    ml_engine = engine or MLEnhancedFusionEngine()
    return ml_engine.analyze(fusion_input)
