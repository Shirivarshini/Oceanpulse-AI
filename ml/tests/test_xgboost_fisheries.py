"""
OceanPulse AI — ML Models
Task 2: XGBoost Fisheries Interface tests.

Done when: valid fisheries features produce a deterministic,
schema-compliant model output and invalid inputs fail safely.

Run with:
    cd ml
    python -m pytest tests/test_xgboost_fisheries.py -v

or, without pytest installed:
    cd ml
    python tests/test_xgboost_fisheries.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fusion_engine.schema import FisheriesFeatures
from models.schema import StockTrendClass, XGBoostOutput
from models.converters import FeatureValidationError
from models.xgboost_fisheries import XGBoostFisheriesInterface, predict_fisheries_trend


def _stable_fisheries():
    return FisheriesFeatures(cpue_trend_pct=-2, vessel_density_index=0.1)


def _declining_fisheries():
    return FisheriesFeatures(cpue_trend_pct=-20, vessel_density_index=0.3)


def _critical_fisheries():
    return FisheriesFeatures(cpue_trend_pct=-45, vessel_density_index=0.9)


# ---------------------------------------------------------------------
# "Done when" criteria, part 1: valid features -> deterministic,
# schema-compliant output.
# ---------------------------------------------------------------------

def test_valid_input_produces_schema_compliant_output():
    engine = XGBoostFisheriesInterface()
    result = engine.predict(_declining_fisheries())

    assert isinstance(result, XGBoostOutput)
    assert result.stock_trend_class in (
        StockTrendClass.STABLE, StockTrendClass.DECLINING, StockTrendClass.CRITICAL_DECLINE
    )
    assert result.confidence is None or 0.0 <= result.confidence <= 1.0
    assert isinstance(result.available, bool)
    print(f"OK schema-compliant output: class={result.stock_trend_class} "
          f"confidence={result.confidence} available={result.available} "
          f"model_version={result.model_version}")


def test_valid_input_is_deterministic():
    engine = XGBoostFisheriesInterface()
    fisheries = _declining_fisheries()

    result_1 = engine.predict(fisheries)
    result_2 = engine.predict(fisheries)

    assert result_1 == result_2
    print(f"OK deterministic: two calls with identical input both "
          f"returned {result_1}")


def test_deterministic_across_fresh_interface_instances():
    fisheries = _critical_fisheries()
    result_a = XGBoostFisheriesInterface().predict(fisheries)
    result_b = XGBoostFisheriesInterface().predict(fisheries)
    assert result_a == result_b
    print("OK deterministic across fresh interface instances")


# ---------------------------------------------------------------------
# "Done when" criteria, part 2: invalid inputs fail safely (a clear,
# typed, catchable error — not a crash).
# ---------------------------------------------------------------------

def test_missing_fisheries_input_fails_safely():
    engine = XGBoostFisheriesInterface()
    try:
        engine.predict(None)
        assert False, "expected FeatureValidationError"
    except FeatureValidationError as e:
        print(f"OK missing input failed safely: {e}")


def test_out_of_range_input_fails_safely():
    engine = XGBoostFisheriesInterface()
    bad_fisheries = FisheriesFeatures(cpue_trend_pct=-20, vessel_density_index=3.0)
    try:
        engine.predict(bad_fisheries)
        assert False, "expected FeatureValidationError"
    except FeatureValidationError as e:
        print(f"OK out-of-range input failed safely: {e}")


def test_non_numeric_input_fails_safely():
    engine = XGBoostFisheriesInterface()
    bad_fisheries = FisheriesFeatures(cpue_trend_pct="collapsing", vessel_density_index=0.5)
    try:
        engine.predict(bad_fisheries)
        assert False, "expected FeatureValidationError"
    except FeatureValidationError as e:
        print(f"OK non-numeric input failed safely: {e}")


# ---------------------------------------------------------------------
# Model availability / version metadata is honest — no trained model
# artifact exists yet, so this must report unavailable, not fake it.
# ---------------------------------------------------------------------

def test_no_trained_model_reports_unavailable_honestly():
    engine = XGBoostFisheriesInterface()
    assert engine.is_available() is False
    result = engine.predict(_stable_fisheries())
    assert result.available is False
    assert result.model_version is None
    print("OK no trained model artifact -> available=False, "
          "model_version=None (heuristic tier active)")


def test_nonexistent_model_path_does_not_crash():
    engine = XGBoostFisheriesInterface(model_path="/tmp/definitely_not_a_real_model.json")
    assert engine.is_available() is False
    result = engine.predict(_stable_fisheries())
    assert isinstance(result, XGBoostOutput)
    print("OK bad model_path handled gracefully, heuristic tier still works")


# ---------------------------------------------------------------------
# Heuristic-tier classification behaves sensibly across the input
# range (sanity check on rule thresholds, not a claim of accuracy).
# ---------------------------------------------------------------------

def test_heuristic_classification_covers_the_three_classes():
    engine = XGBoostFisheriesInterface()

    stable = engine.predict(_stable_fisheries())
    declining = engine.predict(_declining_fisheries())
    critical = engine.predict(_critical_fisheries())

    assert stable.stock_trend_class == StockTrendClass.STABLE
    assert declining.stock_trend_class == StockTrendClass.DECLINING
    assert critical.stock_trend_class == StockTrendClass.CRITICAL_DECLINE
    print(f"OK heuristic covers all three classes: "
          f"stable={stable.stock_trend_class}, "
          f"declining={declining.stock_trend_class}, "
          f"critical={critical.stock_trend_class}")


# ---------------------------------------------------------------------
# Module-level convenience wrapper.
# ---------------------------------------------------------------------

def test_module_level_convenience_function():
    result = predict_fisheries_trend(_declining_fisheries())
    assert isinstance(result, XGBoostOutput)
    print(f"OK predict_fisheries_trend() convenience wrapper: {result}")


if __name__ == "__main__":
    tests = [
        test_valid_input_produces_schema_compliant_output,
        test_valid_input_is_deterministic,
        test_deterministic_across_fresh_interface_instances,
        test_missing_fisheries_input_fails_safely,
        test_out_of_range_input_fails_safely,
        test_non_numeric_input_fails_safely,
        test_no_trained_model_reports_unavailable_honestly,
        test_nonexistent_model_path_does_not_crash,
        test_heuristic_classification_covers_the_three_classes,
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
