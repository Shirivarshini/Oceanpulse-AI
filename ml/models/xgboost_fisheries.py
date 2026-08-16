"""
OceanPulse AI — ML Models
Task 2: XGBoost Fisheries Interface.

Deliverable: XGBoost interface for fisheries/CPUE trend.

Per CLAUDE.md's ML fallback chain:
    1. Trained classifier/matcher   <-- real XGBoost model, when one exists
    2. Similarity/heuristic match
    3. Rule-based scoring            <-- this module's fallback tier
    4. Demo scenario

No trained model has been produced yet (Phase 5's "Add XGBoost
interface" task is about building the *interface*, not training a
model — that requires labeled fisheries data this MVP doesn't have).
Per CLAUDE.md: "Do not claim something is live, deployed, trained, or
tested unless it actually is." So this interface:

  - Tries to load a real trained XGBoost model from MODEL_PATH first.
  - If no model file exists (the current state) or the `xgboost`
    package isn't installed, it falls back to a small, deterministic,
    clearly-labeled rule-based heuristic (tier 3 above) so the product
    still returns a stable, useful output.
  - Always reports `available=False` when the output came from the
    heuristic tier, and `available=True` with a real `model_version`
    only when actual trained-model inference ran. No accuracy,
    precision, or confidence-interval claims are made anywhere — those
    would require an evaluation this MVP hasn't run (see
    implementation_plan.md Phase 5 "Add evaluation script").
"""

import os
from typing import Optional

from fusion_engine.schema import FisheriesFeatures
from .schema import StockTrendClass, XGBoostOutput
from .converters import FeatureValidationError, to_xgboost_input

# Where a trained model would live once one exists. Intentionally not
# committed/created by this task — its absence is what makes the
# fallback tier below active.
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "artifacts", "xgboost_fisheries_model.json"
)

# Heuristic-tier thresholds (rule-based fallback). Mirrors the spirit of
# fusion_engine/scoring.py's CPUE decline bands but is independent —
# this interface must keep working even if fusion_engine changes.
_DECLINE_CRITICAL_PCT = 40.0     # CPUE decline >= 40% alone -> critical
_DECLINE_CRITICAL_WITH_PRESSURE_PCT = 25.0  # or >=25% decline + high vessel pressure
_VESSEL_HIGH_PRESSURE = 0.7
_DECLINE_WARNING_PCT = 15.0      # CPUE decline >= 15% -> declining


class XGBoostFisheriesInterface:
    """
    Wraps fisheries stock / CPUE trend classification behind a stable
    interface, regardless of whether a trained model is actually
    available. One instance loads its model (or confirms none exists)
    once at construction; `predict()` is a pure function of its input
    after that — safe to call repeatedly and deterministic.
    """

    def __init__(self, model_path: str = MODEL_PATH):
        self.model_path = model_path
        self._model = None
        self._model_version: Optional[str] = None
        self._load_model()

    def _load_model(self) -> None:
        """
        Attempts real trained-model loading. Any failure (missing
        package, missing file, corrupt file) leaves self._model = None
        and the interface silently — but honestly — operates in
        heuristic-fallback mode. This is intentionally forgiving: a
        missing model must never crash the app (CLAUDE.md: "The app
        must remain demoable if external dependencies fail").
        """
        if not os.path.exists(self.model_path):
            return

        try:
            import xgboost as xgb  # optional dependency; not required for MVP
        except ImportError:
            return

        try:
            booster = xgb.Booster()
            booster.load_model(self.model_path)
            self._model = booster
            self._model_version = os.path.basename(self.model_path)
        except Exception:
            # Corrupt/incompatible model file — fall back rather than crash.
            self._model = None
            self._model_version = None

    def is_available(self) -> bool:
        """True only if a real trained model was successfully loaded."""
        return self._model is not None

    @property
    def model_version(self) -> Optional[str]:
        """
        Identifier of the currently loaded trained model, or None when
        running in heuristic-fallback mode. Exposed as a public property
        (Task 4 / "Add model availability detection") so callers can
        report availability/version without needing feature data on
        hand to run a full predict() first.
        """
        return self._model_version

    def predict(self, fisheries: FisheriesFeatures) -> XGBoostOutput:
        """
        Prepare fisheries features for inference, then return a stable,
        schema-compliant XGBoostOutput.

        Invalid inputs (missing, non-numeric, out-of-range — see
        converters.py) raise FeatureValidationError. This is the "fail
        safely" behavior: a clear, typed, documented error instead of
        an opaque crash deep inside numeric/model code. Callers (e.g.
        the Fusion Engine's future ML-fallback tier) should catch
        FeatureValidationError and drop to rule-based scoring, per
        CLAUDE.md's fallback chain.
        """
        converted = to_xgboost_input(fisheries)  # raises FeatureValidationError on bad input

        if self.is_available():
            return self._model_predict(converted)
        return self._heuristic_predict(converted)

    # -- real trained-model inference (used once a model exists) -----

    def _model_predict(self, converted: dict) -> XGBoostOutput:
        import xgboost as xgb  # already confirmed importable in _load_model

        dmatrix = xgb.DMatrix([[converted[name] for name in
                                 ("cpue_trend_pct", "vessel_density_index")]])
        raw = self._model.predict(dmatrix)[0]

        classes = [StockTrendClass.STABLE, StockTrendClass.DECLINING,
                   StockTrendClass.CRITICAL_DECLINE]
        # raw is expected to be a class index or a probability vector,
        # depending on how the (currently nonexistent) model was
        # trained. Handle both shapes defensively.
        try:
            class_index = int(raw)
            confidence = None
        except TypeError:
            class_index = int(raw.argmax())
            confidence = round(float(raw[class_index]), 2)

        return XGBoostOutput(
            stock_trend_class=classes[class_index],
            confidence=confidence,
            model_version=self._model_version,
            available=True,
        )

    # -- heuristic fallback tier (active until a model is trained) ---

    def _heuristic_predict(self, converted: dict) -> XGBoostOutput:
        """
        Deterministic, rule-based CPUE trend classification. This is
        NOT a trained model — `available` stays False and no accuracy
        metric is attached, since none has been measured.
        """
        decline_pct = -converted["cpue_trend_pct"]  # negative trend => positive decline
        vessel_density = converted["vessel_density_index"]

        if (decline_pct >= _DECLINE_CRITICAL_PCT or
                (decline_pct >= _DECLINE_CRITICAL_WITH_PRESSURE_PCT
                 and vessel_density >= _VESSEL_HIGH_PRESSURE)):
            trend_class = StockTrendClass.CRITICAL_DECLINE
        elif decline_pct >= _DECLINE_WARNING_PCT:
            trend_class = StockTrendClass.DECLINING
        else:
            trend_class = StockTrendClass.STABLE

        # A small, deterministic "how clear-cut is this call" heuristic
        # score — NOT a model confidence and NOT a measured metric.
        # Distance from the nearest threshold, normalized to 0.50-0.75.
        thresholds = [_DECLINE_WARNING_PCT, _DECLINE_CRITICAL_PCT]
        nearest_gap = min(abs(decline_pct - t) for t in thresholds)
        heuristic_score = round(min(0.75, 0.50 + min(nearest_gap, 25.0) / 100.0), 2)

        return XGBoostOutput(
            stock_trend_class=trend_class,
            confidence=heuristic_score,
            model_version=None,
            available=False,
        )


def predict_fisheries_trend(
    fisheries: FisheriesFeatures,
    interface: Optional[XGBoostFisheriesInterface] = None,
) -> XGBoostOutput:
    """
    Module-level convenience wrapper. Pass an existing
    XGBoostFisheriesInterface to avoid repeated model-load attempts
    across many calls; otherwise a fresh one is created (cheap, since
    the model file doesn't exist yet — the load attempt is a single
    os.path.exists() check).
    """
    engine = interface or XGBoostFisheriesInterface()
    return engine.predict(fisheries)
