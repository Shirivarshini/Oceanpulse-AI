"""
OceanPulse AI — ML Models
Task 4: Integrate ML Outputs with the Fusion Engine — tests.

Deliverable: optional ML-enhanced Fusion Engine.
Done when: the Fusion Engine can use ML when available and still
produces valid results when ML is disabled.

Run with:
    cd ml
    python -m pytest tests/test_ml_fusion_engine.py -v

or, without pytest installed:
    cd ml
    python tests/test_ml_fusion_engine.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fusion_engine.fusion import FusionEngine, index_to_level
from fusion_engine.schema import (
    FusionInput, OceanFeatures, FisheriesFeatures, MolecularFeatures,
    SourceStatus,
)
from fusion_engine.demo_scenarios import SCENARIOS, get_scenario
from models.schema import IsolationForestOutput, StockTrendClass, XGBoostOutput
from models.converters import FeatureValidationError
from models.ml_fusion_engine import (
    MLEnhancedFusionEngine,
    MLFusionResult,
    analyze_with_ml,
)


# ---------------------------------------------------------------------
# Fake interfaces — let us exercise the "ML available" branch without
# needing an actual trained model artifact on disk. Match the same
# public surface (`is_available`, `model_version`, `predict`) real
# interfaces expose.
# ---------------------------------------------------------------------

class _FakeUnavailableXGB:
    def is_available(self):
        return False

    model_version = None

    def predict(self, fisheries):
        return XGBoostOutput(available=False, model_version=None)


class _FakeXGB:
    def __init__(self, stock_trend_class, confidence=0.8, version="fake-xgb-v1"):
        self._class = stock_trend_class
        self._confidence = confidence
        self.model_version = version

    def is_available(self):
        return True

    def predict(self, fisheries):
        return XGBoostOutput(
            stock_trend_class=self._class,
            confidence=self._confidence,
            model_version=self.model_version,
            available=True,
        )


class _FakeRaisingXGB:
    """Simulates the real interface's behavior on invalid input."""
    model_version = None

    def is_available(self):
        return True

    def predict(self, fisheries):
        raise FeatureValidationError("simulated bad input")


class _FakeUnavailableIso:
    def is_available(self):
        return False

    model_version = None

    def predict(self, ocean, fisheries, molecular):
        return IsolationForestOutput(available=False, model_version=None)


class _FakeIso:
    def __init__(self, score, is_anomaly, version="fake-iso-v1"):
        self._score = score
        self._is_anomaly = is_anomaly
        self.model_version = version

    def is_available(self):
        return True

    def predict(self, ocean, fisheries, molecular):
        return IsolationForestOutput(
            normalized_anomaly_score=self._score,
            is_anomaly=self._is_anomaly,
            model_version=self.model_version,
            available=True,
        )


def _sample_input():
    return FusionInput(
        region_id="gulf-of-mannar",
        ocean=OceanFeatures(sst_anomaly_c=1.8, chlorophyll_a_anomaly_pct=20,
                             source=SourceStatus.DEMO),
        fisheries=FisheriesFeatures(cpue_trend_pct=-30, vessel_density_index=0.5,
                                     source=SourceStatus.DEMO),
        molecular=MolecularFeatures(species_richness=60, baseline_richness=100,
                                     rare_taxa_detected=1, invasive_taxa_detected=0,
                                     sample_quality=0.9, source=SourceStatus.DEMO),
    )


def _no_ml_engine():
    return MLEnhancedFusionEngine(
        xgboost_interface=_FakeUnavailableXGB(),
        isolation_forest_interface=_FakeUnavailableIso(),
    )


# ---------------------------------------------------------------------
# "Done when" criteria, part 1: ML disabled -> valid results, unchanged
# from the plain rule-based FusionEngine.
# ---------------------------------------------------------------------

def test_ml_disabled_matches_plain_fusion_engine_exactly():
    fusion_input = _sample_input()
    base = FusionEngine().analyze(fusion_input)
    ml_result = _no_ml_engine().analyze(fusion_input)

    assert isinstance(ml_result, MLFusionResult)
    assert ml_result.index == base.index
    assert ml_result.level == base.level
    assert ml_result.confidence == base.confidence
    assert ml_result.factors == base.factors
    assert ml_result.timeline == base.timeline
    assert ml_result.sources == base.sources
    assert ml_result.ml_enhanced is False
    print(f"OK ML disabled == plain FusionEngine: index={ml_result.index} "
          f"level={ml_result.level} confidence={ml_result.confidence}")


def test_demo_scenarios_unchanged_when_no_trained_models():
    """
    No trained model artifacts ship with this MVP today, so
    MLEnhancedFusionEngine (using its REAL, default interfaces — not
    the fakes above) must reproduce the exact contract values for all
    three demo scenarios, unchanged. This is the "do not break
    existing demo scenarios" requirement.
    """
    engine = MLEnhancedFusionEngine()  # real interfaces, no artifacts on disk
    expected = {
        "healthy_reef": (22, "STABLE"),
        "declining_fishery": (55, "WATCH"),
        "coral_bleaching": (88, "CRITICAL"),
    }
    for name, (expected_index, expected_level) in expected.items():
        result = engine.analyze(get_scenario(name))
        assert result.index == expected_index, (
            f"{name}: expected index {expected_index}, got {result.index}"
        )
        assert result.level == expected_level, (
            f"{name}: expected level {expected_level}, got {result.level}"
        )
        assert result.ml_enhanced is False
        print(f"OK {name} unchanged with no trained models: "
              f"index={result.index} level={result.level}")


def test_model_status_reports_unavailable_honestly_with_no_artifacts():
    engine = MLEnhancedFusionEngine()
    status = engine.model_status()
    assert status["xgboost_fisheries"]["available"] is False
    assert status["xgboost_fisheries"]["model_version"] is None
    assert status["isolation_forest_anomaly"]["available"] is False
    assert status["isolation_forest_anomaly"]["model_version"] is None
    print(f"OK model_status honest with no artifacts: {status}")


# ---------------------------------------------------------------------
# "Done when" criteria, part 2: ML available -> combined output.
# ---------------------------------------------------------------------

def test_ml_available_adds_factor_and_raises_index_for_critical_decline():
    fusion_input = _sample_input()
    base = FusionEngine().analyze(fusion_input)

    engine = MLEnhancedFusionEngine(
        xgboost_interface=_FakeXGB(StockTrendClass.CRITICAL_DECLINE),
        isolation_forest_interface=_FakeUnavailableIso(),
    )
    result = engine.analyze(fusion_input)

    assert result.ml_enhanced is True
    assert result.index > base.index
    assert result.index == max(0, min(100, base.index + 10))
    assert any(f["name"] == "ML Fisheries Stock Classification" for f in result.factors)
    # base factors are preserved, not replaced
    for f in base.factors:
        assert f in result.factors
    assert result.confidence >= base.confidence
    assert result.timeline == base.timeline
    assert result.sources == base.sources
    print(f"OK ML-available (XGBoost critical_decline): base index={base.index} "
          f"-> ml index={result.index}, confidence {base.confidence} -> {result.confidence}")


def test_ml_available_stable_class_boosts_confidence_without_changing_index():
    # Use a sparser input (no molecular signal) so base confidence sits
    # below the 0.98 ceiling and a confidence boost is actually visible
    # — the full-signal _sample_input() already confidence-caps at 0.98.
    fusion_input = FusionInput(
        region_id="gulf-of-mannar",
        ocean=OceanFeatures(sst_anomaly_c=1.8, source=SourceStatus.DEMO),
        fisheries=FisheriesFeatures(cpue_trend_pct=-30, vessel_density_index=0.5,
                                     source=SourceStatus.DEMO),
        molecular=None,
    )
    base = FusionEngine().analyze(fusion_input)

    engine = MLEnhancedFusionEngine(
        xgboost_interface=_FakeXGB(StockTrendClass.STABLE),
        isolation_forest_interface=_FakeUnavailableIso(),
    )
    result = engine.analyze(fusion_input)

    assert result.ml_enhanced is True
    assert result.index == base.index
    assert result.level == base.level
    assert result.confidence > base.confidence
    assert not any(f["name"] == "ML Fisheries Stock Classification" for f in result.factors)
    print(f"OK ML-available (XGBoost stable): index unchanged at {result.index}, "
          f"confidence {base.confidence} -> {result.confidence}")


def test_isolation_forest_anomaly_adds_factor():
    fusion_input = _sample_input()
    base = FusionEngine().analyze(fusion_input)

    engine = MLEnhancedFusionEngine(
        xgboost_interface=_FakeUnavailableXGB(),
        isolation_forest_interface=_FakeIso(score=0.9, is_anomaly=True),
    )
    result = engine.analyze(fusion_input)

    assert result.ml_enhanced is True
    assert result.index > base.index
    assert any(f["name"] == "ML Ecosystem Anomaly Detected" for f in result.factors)
    print(f"OK IsolationForest anomaly adds factor: index {base.index} -> {result.index}")


def test_isolation_forest_no_anomaly_no_index_change():
    fusion_input = _sample_input()
    base = FusionEngine().analyze(fusion_input)

    engine = MLEnhancedFusionEngine(
        xgboost_interface=_FakeUnavailableXGB(),
        isolation_forest_interface=_FakeIso(score=0.1, is_anomaly=False),
    )
    result = engine.analyze(fusion_input)

    assert result.index == base.index
    assert result.confidence >= base.confidence
    print("OK IsolationForest no-anomaly: index unchanged, confidence non-decreasing")


def test_both_models_available_combine_together():
    fusion_input = _sample_input()
    base = FusionEngine().analyze(fusion_input)

    engine = MLEnhancedFusionEngine(
        xgboost_interface=_FakeXGB(StockTrendClass.DECLINING),
        isolation_forest_interface=_FakeIso(score=0.5, is_anomaly=True),
    )
    result = engine.analyze(fusion_input)

    factor_names = {f["name"] for f in result.factors}
    assert "ML Fisheries Stock Classification" in factor_names
    assert "ML Ecosystem Anomaly Detected" in factor_names
    assert result.index > base.index
    assert result.model_status["xgboost_fisheries"]["available"] is True
    assert result.model_status["isolation_forest_anomaly"]["available"] is True
    print(f"OK both models combine: base={base.index} -> combined={result.index}, "
          f"factors={sorted(factor_names)}")


# ---------------------------------------------------------------------
# Index classification bands (API_CONTRACT.md section 3) must still
# hold for ML-enhanced results, including at the 0/100 clamp edges.
# ---------------------------------------------------------------------

def test_index_classification_bands_preserved_for_ml_enhanced_result():
    fusion_input = _sample_input()
    engine = MLEnhancedFusionEngine(
        xgboost_interface=_FakeXGB(StockTrendClass.CRITICAL_DECLINE),
        isolation_forest_interface=_FakeIso(score=1.0, is_anomaly=True),
    )
    result = engine.analyze(fusion_input)
    assert result.level == index_to_level(result.index)
    print(f"OK ML-enhanced result still classified via index_to_level(): "
          f"index={result.index} level={result.level}")


def test_ml_enhanced_index_still_clamped_0_to_100():
    extreme = FusionInput(
        region_id="extreme-region",
        ocean=OceanFeatures(sst_anomaly_c=10, chlorophyll_a_anomaly_pct=500,
                             source=SourceStatus.DEMO),
        fisheries=FisheriesFeatures(cpue_trend_pct=-90, vessel_density_index=1.0,
                                     source=SourceStatus.DEMO),
        molecular=MolecularFeatures(species_richness=0, baseline_richness=100,
                                     rare_taxa_detected=0, invasive_taxa_detected=5,
                                     sample_quality=1.0, source=SourceStatus.DEMO),
    )
    engine = MLEnhancedFusionEngine(
        xgboost_interface=_FakeXGB(StockTrendClass.CRITICAL_DECLINE),
        isolation_forest_interface=_FakeIso(score=1.0, is_anomaly=True),
    )
    result = engine.analyze(extreme)
    assert 0 <= result.index <= 100
    assert result.level == "CRITICAL"
    print(f"OK ML-enhanced extreme input still clamps to 0-100: index={result.index}")


# ---------------------------------------------------------------------
# Availability detection must not crash the pipeline on missing or
# invalid signals — this layer is the boundary that guarantees
# analyze() never raises regardless of what the wrapped interfaces do.
# ---------------------------------------------------------------------

def test_missing_fisheries_signal_skips_xgboost_without_crashing():
    fusion_input = FusionInput(
        region_id="ocean-only",
        ocean=OceanFeatures(sst_anomaly_c=1.0, source=SourceStatus.DEMO),
        fisheries=None,
        molecular=None,
    )
    engine = MLEnhancedFusionEngine(
        xgboost_interface=_FakeXGB(StockTrendClass.CRITICAL_DECLINE),
        isolation_forest_interface=_FakeUnavailableIso(),
    )
    result = engine.analyze(fusion_input)
    assert result.model_status["xgboost_fisheries"]["reason"] == "no_fisheries_signal"
    assert not any(f["name"] == "ML Fisheries Stock Classification" for f in result.factors)
    print("OK missing fisheries signal: XGBoost skipped cleanly, no crash")


def test_xgboost_raising_feature_validation_error_does_not_crash_pipeline():
    fusion_input = _sample_input()
    engine = MLEnhancedFusionEngine(
        xgboost_interface=_FakeRaisingXGB(),
        isolation_forest_interface=_FakeUnavailableIso(),
    )
    result = engine.analyze(fusion_input)
    assert result.model_status["xgboost_fisheries"]["available"] is False
    assert "invalid_input" in result.model_status["xgboost_fisheries"]["reason"]
    print("OK XGBoost FeatureValidationError caught and reported, pipeline still returns a result")


# ---------------------------------------------------------------------
# Determinism — same input, same output, same rule as the base engine.
# ---------------------------------------------------------------------

def test_ml_enhanced_result_is_deterministic():
    fusion_input = _sample_input()
    engine = MLEnhancedFusionEngine(
        xgboost_interface=_FakeXGB(StockTrendClass.DECLINING),
        isolation_forest_interface=_FakeIso(score=0.6, is_anomaly=True),
    )
    result_1 = engine.analyze(fusion_input)
    result_2 = engine.analyze(fusion_input)
    assert result_1.index == result_2.index
    assert result_1.level == result_2.level
    assert result_1.confidence == result_2.confidence
    assert result_1.factors == result_2.factors
    print("OK ML-enhanced determinism: two runs with identical input and "
          "identical (fake) model outputs match")


# ---------------------------------------------------------------------
# Module-level convenience wrapper.
# ---------------------------------------------------------------------

def test_module_level_convenience_function():
    result = analyze_with_ml(_sample_input(), engine=_no_ml_engine())
    assert isinstance(result, MLFusionResult)
    print(f"OK analyze_with_ml() convenience wrapper: index={result.index}")


if __name__ == "__main__":
    tests = [
        test_ml_disabled_matches_plain_fusion_engine_exactly,
        test_demo_scenarios_unchanged_when_no_trained_models,
        test_model_status_reports_unavailable_honestly_with_no_artifacts,
        test_ml_available_adds_factor_and_raises_index_for_critical_decline,
        test_ml_available_stable_class_boosts_confidence_without_changing_index,
        test_isolation_forest_anomaly_adds_factor,
        test_isolation_forest_no_anomaly_no_index_change,
        test_both_models_available_combine_together,
        test_index_classification_bands_preserved_for_ml_enhanced_result,
        test_ml_enhanced_index_still_clamped_0_to_100,
        test_missing_fisheries_signal_skips_xgboost_without_crashing,
        test_xgboost_raising_feature_validation_error_does_not_crash_pipeline,
        test_ml_enhanced_result_is_deterministic,
        test_module_level_convenience_function,
    ]
    failures = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failures += 1
            print(f"FAIL {t.__name__}: {e}")
    print()
    if failures:
        print(f"{failures} test(s) failed.")
        sys.exit(1)
    print(f"All {len(tests)} tests passed.")
