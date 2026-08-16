"""
OceanPulse AI — ML Models
Task 3: IsolationForest Ecosystem Anomaly Interface tests.

Done when: normal and anomalous inputs can be processed and the result
can be consumed by the Fusion Engine.

Run with:
    cd ml
    python -m pytest tests/test_isolation_forest_anomaly.py -v

or, without pytest installed:
    cd ml
    python tests/test_isolation_forest_anomaly.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fusion_engine.schema import OceanFeatures, FisheriesFeatures, MolecularFeatures
from fusion_engine.demo_scenarios import SCENARIOS
from models.schema import IsolationForestOutput
from models.isolation_forest_anomaly import (
    IsolationForestAnomalyInterface,
    detect_ecosystem_anomaly,
)


def _normal_inputs():
    return (
        OceanFeatures(sst_anomaly_c=0.2, chlorophyll_a_anomaly_pct=5, salinity_anomaly_psu=0.1),
        FisheriesFeatures(cpue_trend_pct=-3, vessel_density_index=0.1),
        MolecularFeatures(species_richness=95, baseline_richness=100),
    )


def _anomalous_inputs():
    return (
        OceanFeatures(sst_anomaly_c=3.0, chlorophyll_a_anomaly_pct=200, salinity_anomaly_psu=-3),
        FisheriesFeatures(cpue_trend_pct=-60, vessel_density_index=0.95),
        MolecularFeatures(species_richness=30, baseline_richness=100),
    )


# ---------------------------------------------------------------------
# "Done when" criteria, part 1: normal and anomalous inputs can both
# be processed.
# ---------------------------------------------------------------------

def test_normal_input_is_processed():
    engine = IsolationForestAnomalyInterface()
    ocean, fisheries, molecular = _normal_inputs()
    result = engine.predict(ocean, fisheries, molecular)

    assert isinstance(result, IsolationForestOutput)
    assert result.normalized_anomaly_score is not None
    assert 0.0 <= result.normalized_anomaly_score <= 1.0
    assert result.is_anomaly is False
    print(f"OK normal input processed: score={result.normalized_anomaly_score} "
          f"is_anomaly={result.is_anomaly}")


def test_anomalous_input_is_processed_and_flagged():
    engine = IsolationForestAnomalyInterface()
    ocean, fisheries, molecular = _anomalous_inputs()
    result = engine.predict(ocean, fisheries, molecular)

    assert isinstance(result, IsolationForestOutput)
    assert result.normalized_anomaly_score is not None
    assert result.is_anomaly is True
    print(f"OK anomalous input processed and flagged: "
          f"score={result.normalized_anomaly_score} is_anomaly={result.is_anomaly}")


def test_anomalous_score_higher_than_normal_score():
    engine = IsolationForestAnomalyInterface()
    normal_result = engine.predict(*_normal_inputs())
    anomalous_result = engine.predict(*_anomalous_inputs())
    assert anomalous_result.normalized_anomaly_score > normal_result.normalized_anomaly_score
    print(f"OK anomalous score ({anomalous_result.normalized_anomaly_score}) > "
          f"normal score ({normal_result.normalized_anomaly_score})")


def test_deterministic_across_repeated_calls():
    engine = IsolationForestAnomalyInterface()
    ocean, fisheries, molecular = _anomalous_inputs()
    result_1 = engine.predict(ocean, fisheries, molecular)
    result_2 = engine.predict(ocean, fisheries, molecular)
    assert result_1 == result_2
    print("OK deterministic across repeated calls with identical input")


# ---------------------------------------------------------------------
# "Done when" criteria, part 2: the result can be consumed by the
# Fusion Engine — proven here by feeding the Fusion Engine's own demo
# scenario inputs (fusion_engine.schema objects, unmodified) straight
# through this interface.
# ---------------------------------------------------------------------

def test_fusion_engine_demo_scenario_inputs_are_consumable():
    engine = IsolationForestAnomalyInterface()
    for name, fusion_input in SCENARIOS.items():
        result = engine.predict(
            fusion_input.ocean, fusion_input.fisheries, fusion_input.molecular
        )
        assert isinstance(result, IsolationForestOutput)
        assert result.normalized_anomaly_score is not None
        assert isinstance(result.is_anomaly, bool)
        print(f"OK {name}: score={result.normalized_anomaly_score} "
              f"is_anomaly={result.is_anomaly} (consumable IsolationForestOutput)")


def test_coral_bleaching_scenario_flags_as_anomalous():
    """The primary judge-demo scenario should read as the clear
    ecosystem anomaly among the three."""
    engine = IsolationForestAnomalyInterface()
    result = engine.predict(
        SCENARIOS["coral_bleaching"].ocean,
        SCENARIOS["coral_bleaching"].fisheries,
        SCENARIOS["coral_bleaching"].molecular,
    )
    assert result.is_anomaly is True
    print(f"OK coral_bleaching flags as anomalous: score={result.normalized_anomaly_score}")


# ---------------------------------------------------------------------
# Handle unavailable model/input data without breaking the pipeline —
# invalid/incomplete input never raises, it resolves to a safe
# "unavailable" output.
# ---------------------------------------------------------------------

def test_missing_signal_group_does_not_raise():
    engine = IsolationForestAnomalyInterface()
    ocean, fisheries, molecular = _normal_inputs()
    result = engine.predict(None, fisheries, molecular)  # ocean missing
    assert isinstance(result, IsolationForestOutput)
    assert result.available is False
    assert result.normalized_anomaly_score is None
    assert result.is_anomaly is None
    print("OK missing signal group handled without raising: "
          f"{result}")


def test_out_of_range_value_does_not_raise():
    engine = IsolationForestAnomalyInterface()
    bad_ocean = OceanFeatures(sst_anomaly_c=999, chlorophyll_a_anomaly_pct=5)
    _, fisheries, molecular = _normal_inputs()
    result = engine.predict(bad_ocean, fisheries, molecular)
    assert isinstance(result, IsolationForestOutput)
    assert result.available is False
    print(f"OK out-of-range value handled without raising: {result}")


def test_non_numeric_value_does_not_raise():
    engine = IsolationForestAnomalyInterface()
    bad_ocean = OceanFeatures(sst_anomaly_c="hot", chlorophyll_a_anomaly_pct=5)
    _, fisheries, molecular = _normal_inputs()
    result = engine.predict(bad_ocean, fisheries, molecular)
    assert isinstance(result, IsolationForestOutput)
    assert result.available is False
    print(f"OK non-numeric value handled without raising: {result}")


def test_nonexistent_model_path_does_not_crash():
    engine = IsolationForestAnomalyInterface(model_path="/tmp/not_a_real_model.joblib")
    assert engine.is_available() is False
    result = engine.predict(*_normal_inputs())
    assert isinstance(result, IsolationForestOutput)
    print("OK bad model_path handled gracefully, heuristic tier still works")


# ---------------------------------------------------------------------
# Model availability / version metadata is honest.
# ---------------------------------------------------------------------

def test_no_trained_model_reports_unavailable_honestly():
    engine = IsolationForestAnomalyInterface()
    assert engine.is_available() is False
    result = engine.predict(*_normal_inputs())
    assert result.model_version is None
    print("OK no trained model artifact -> model_version=None "
          "(heuristic tier active)")


# ---------------------------------------------------------------------
# Module-level convenience wrapper.
# ---------------------------------------------------------------------

def test_module_level_convenience_function():
    result = detect_ecosystem_anomaly(*_anomalous_inputs())
    assert isinstance(result, IsolationForestOutput)
    print(f"OK detect_ecosystem_anomaly() convenience wrapper: {result}")


if __name__ == "__main__":
    tests = [
        test_normal_input_is_processed,
        test_anomalous_input_is_processed_and_flagged,
        test_anomalous_score_higher_than_normal_score,
        test_deterministic_across_repeated_calls,
        test_fusion_engine_demo_scenario_inputs_are_consumable,
        test_coral_bleaching_scenario_flags_as_anomalous,
        test_missing_signal_group_does_not_raise,
        test_out_of_range_value_does_not_raise,
        test_non_numeric_value_does_not_raise,
        test_nonexistent_model_path_does_not_crash,
        test_no_trained_model_reports_unavailable_honestly,
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
