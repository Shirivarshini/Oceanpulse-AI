"""
OceanPulse AI — ML Models
Task 3: IsolationForest Ecosystem Anomaly Interface.

Deliverable: ecosystem anomaly detector.

Same ML fallback tier structure as Task 2's XGBoost fisheries
interface (see xgboost_fisheries.py), per CLAUDE.md:

    1. Trained classifier/matcher   <-- real IsolationForest model, once one exists
    2. Similarity/heuristic match
    3. Rule-based scoring            <-- current active tier (no model trained yet)
    4. Demo scenario

No trained model artifact exists yet — training one requires labeled
"normal vs. anomalous" ecosystem data this MVP doesn't have. Per
CLAUDE.md's "never fabricate ... model metrics" / "do not claim
trained ... unless it actually is", this interface honestly reports
`available=False` until a real model is placed at MODEL_PATH.

Unlike the XGBoost interface, this one does NOT propagate a validation
error to the caller. Per this task's explicit requirement — "Handle
unavailable model/input data without breaking the pipeline" — an
unavailable model or invalid/incomplete input both resolve to the same
safe, schema-compliant "unavailable" output, so a consumer (the Fusion
Engine) can check `result.available` and move on without needing a
try/except around every call.
"""

import os
from typing import Optional

from fusion_engine.schema import FisheriesFeatures, MolecularFeatures, OceanFeatures
from .schema import ISOLATION_FOREST_FEATURE_SPECS, IsolationForestOutput
from .converters import FeatureValidationError, to_isolation_forest_input, isolation_forest_feature_vector

# Where a trained model would live once one exists. Its absence is
# what keeps the heuristic fallback tier active.
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "artifacts", "isolation_forest_ecosystem_model.joblib"
)

# Heuristic-tier threshold (rule-based fallback). A feature's magnitude
# is normalized against its own documented range from
# ISOLATION_FOREST_FEATURE_SPECS, averaged across all features, and
# compared to this threshold. Calibrated so the coral_bleaching demo
# scenario (score ~0.42) flags as anomalous while healthy_reef (~0.12)
# and declining_fishery (~0.24) do not.
_ANOMALY_THRESHOLD = 0.35


class IsolationForestAnomalyInterface:
    """
    Wraps ecosystem-wide anomaly detection behind a stable interface.
    One instance loads its model (or confirms none exists) once at
    construction; `predict()` is a pure function of its input after
    that — safe to call repeatedly and deterministic.
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
        and the interface operates in heuristic-fallback mode instead
        of crashing (CLAUDE.md: "The app must remain demoable if
        external dependencies fail").
        """
        if not os.path.exists(self.model_path):
            return

        try:
            import joblib  # optional dependency; not required for MVP
        except ImportError:
            return

        try:
            self._model = joblib.load(self.model_path)
            self._model_version = os.path.basename(self.model_path)
        except Exception:
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

    def predict(
        self,
        ocean: Optional[OceanFeatures],
        fisheries: Optional[FisheriesFeatures],
        molecular: Optional[MolecularFeatures],
    ) -> IsolationForestOutput:
        """
        Prepare ecosystem features and return a stable, schema-compliant
        IsolationForestOutput — for BOTH normal and anomalous inputs,
        and even when a signal is missing/invalid or no model is
        loaded. Never raises: an unavailable model or unusable input
        both resolve to `available=False` with score/flag left None,
        which the Fusion Engine can safely check and move past.
        """
        try:
            converted = to_isolation_forest_input(ocean, fisheries, molecular)
        except FeatureValidationError:
            return IsolationForestOutput(
                normalized_anomaly_score=None,
                is_anomaly=None,
                model_version=self._model_version,
                available=False,
            )

        if self.is_available():
            return self._model_predict(converted)
        return self._heuristic_predict(converted)

    # -- real trained-model inference (used once a model exists) -----

    def _model_predict(self, converted: dict) -> IsolationForestOutput:
        vector = [isolation_forest_feature_vector(converted)]

        # scikit-learn convention: predict() gives 1 (normal) / -1
        # (anomaly); score_samples() gives higher = more normal. Both
        # are re-expressed here in the schema's own terms.
        is_anomaly = bool(self._model.predict(vector)[0] == -1)
        raw_score = float(self._model.score_samples(vector)[0])
        # raw_score typically falls roughly in [-0.5, 0.5]; flip sign
        # (higher = more anomalous) and clip into 0.0-1.0.
        normalized_score = round(max(0.0, min(1.0, 0.5 - raw_score)), 2)

        return IsolationForestOutput(
            normalized_anomaly_score=normalized_score,
            is_anomaly=is_anomaly,
            model_version=self._model_version,
            available=True,
        )

    # -- heuristic fallback tier (active until a model is trained) ---

    def _heuristic_predict(self, converted: dict) -> IsolationForestOutput:
        """
        Deterministic, rule-based ecosystem anomaly scoring. This is
        NOT a trained model — `available` stays False. Each feature's
        magnitude is normalized against its own documented range, then
        averaged into a single 0.0-1.0 score.
        """
        magnitudes = []
        for spec in ISOLATION_FOREST_FEATURE_SPECS:
            value = converted[spec.name]
            denom = max(abs(spec.min_value), abs(spec.max_value))
            magnitudes.append(min(1.0, abs(value) / denom) if denom > 0 else 0.0)

        score = round(sum(magnitudes) / len(magnitudes), 3)
        is_anomaly = score >= _ANOMALY_THRESHOLD

        return IsolationForestOutput(
            normalized_anomaly_score=score,
            is_anomaly=is_anomaly,
            model_version=None,
            available=False,
        )


def detect_ecosystem_anomaly(
    ocean: Optional[OceanFeatures],
    fisheries: Optional[FisheriesFeatures],
    molecular: Optional[MolecularFeatures],
    interface: Optional[IsolationForestAnomalyInterface] = None,
) -> IsolationForestOutput:
    """
    Module-level convenience wrapper. Pass an existing
    IsolationForestAnomalyInterface to avoid repeated model-load
    attempts across many calls; otherwise a fresh one is created.
    """
    engine = interface or IsolationForestAnomalyInterface()
    return engine.predict(ocean, fisheries, molecular)
