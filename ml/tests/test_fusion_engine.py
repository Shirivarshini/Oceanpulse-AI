"""
OceanPulse AI — Insight Fusion Engine tests.

Run with:
    cd ml
    python -m pytest tests/test_fusion_engine.py -v

or, without pytest installed:
    cd ml
    python tests/test_fusion_engine.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fusion_engine.fusion import FusionEngine, index_to_level
from fusion_engine.schema import (
    FusionInput, OceanFeatures, FisheriesFeatures, MolecularFeatures,
    SourceStatus,
)
from fusion_engine.demo_scenarios import (
    HEALTHY_REEF, DECLINING_FISHERY, CORAL_BLEACHING, get_scenario,
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


# ---------------------------------------------------------------------
# Task 1 success criteria: "The same input produces the same index on
# repeated executions." This is the exact check Member 3 runs at Hour 5.
# ---------------------------------------------------------------------

def test_determinism_same_input_same_output():
    engine = FusionEngine()
    fusion_input = _sample_input()

    result_1 = engine.analyze(fusion_input)
    result_2 = engine.analyze(fusion_input)

    assert result_1.index == result_2.index
    assert result_1.level == result_2.level
    assert result_1.confidence == result_2.confidence
    assert result_1.factors == result_2.factors
    assert result_1.sources == result_2.sources
    print(f"OK determinism: index={result_1.index} level={result_1.level} "
          f"confidence={result_1.confidence} (matched across 2 runs)")


def test_determinism_across_fresh_engine_instances():
    """Same input through two independent FusionEngine() instances must
    still agree — the engine must hold no cross-call state."""
    fusion_input = _sample_input()
    result_a = FusionEngine().analyze(fusion_input)
    result_b = FusionEngine().analyze(fusion_input)
    assert result_a.index == result_b.index
    assert result_a.factors == result_b.factors
    print("OK determinism across fresh engine instances")


# ---------------------------------------------------------------------
# Index level bands (API_CONTRACT.md section 3)
# ---------------------------------------------------------------------

def test_index_level_bands():
    assert index_to_level(0) == "STABLE"
    assert index_to_level(29) == "STABLE"
    assert index_to_level(30) == "WATCH"
    assert index_to_level(59) == "WATCH"
    assert index_to_level(60) == "STRESSED"
    assert index_to_level(79) == "STRESSED"
    assert index_to_level(80) == "CRITICAL"
    assert index_to_level(100) == "CRITICAL"
    print("OK index level bands match API_CONTRACT.md section 3")


def test_index_is_clamped_0_to_100():
    engine = FusionEngine()
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
    result = engine.analyze(extreme)
    assert 0 <= result.index <= 100
    print(f"OK clamped index for extreme input: {result.index}")


# ---------------------------------------------------------------------
# Demo scenarios must match API_CONTRACT.md section 6 exactly.
# ---------------------------------------------------------------------

def test_demo_scenarios_match_contract():
    engine = FusionEngine()

    expected = {
        "healthy_reef": (22, "STABLE"),
        "declining_fishery": (55, "WATCH"),
        "coral_bleaching": (88, "CRITICAL"),
    }

    for name, (expected_index, expected_level) in expected.items():
        scenario_input = get_scenario(name)
        result = engine.analyze(scenario_input)
        assert result.index == expected_index, (
            f"{name}: expected index {expected_index}, got {result.index}"
        )
        assert result.level == expected_level, (
            f"{name}: expected level {expected_level}, got {result.level}"
        )
        print(f"OK {name}: index={result.index} level={result.level} "
              f"confidence={result.confidence}")


def test_coral_bleaching_timeline_shows_escalation():
    engine = FusionEngine()
    result = engine.analyze(CORAL_BLEACHING)
    indices = [point["index"] for point in result.timeline]
    assert indices == [28, 55, 88], f"expected [28, 55, 88], got {indices}"
    print(f"OK coral_bleaching timeline escalation: {indices}")


def test_unknown_scenario_raises_key_error():
    try:
        get_scenario("not_a_real_scenario")
        assert False, "expected KeyError"
    except KeyError:
        print("OK unknown scenario raises KeyError (Backend maps this to "
              "INVALID_SCENARIO)")


# ---------------------------------------------------------------------
# Graceful degradation — missing signal categories
# ---------------------------------------------------------------------

def test_missing_categories_degrade_confidence_not_crash():
    engine = FusionEngine()
    ocean_only = FusionInput(
        region_id="sparse-region",
        ocean=OceanFeatures(sst_anomaly_c=1.0, source=SourceStatus.DEMO),
        fisheries=None,
        molecular=None,
    )
    result = engine.analyze(ocean_only)
    assert result.index >= 0
    assert result.confidence < FusionEngine()._confidence(
        _sample_input(),
        _sample_input().ocean, _sample_input().fisheries, _sample_input().molecular,
    )
    print(f"OK sparse-data region: index={result.index} "
          f"confidence={result.confidence} (lower than fully-covered region)")


if __name__ == "__main__":
    tests = [
        test_determinism_same_input_same_output,
        test_determinism_across_fresh_engine_instances,
        test_index_level_bands,
        test_index_is_clamped_0_to_100,
        test_demo_scenarios_match_contract,
        test_coral_bleaching_timeline_shows_escalation,
        test_unknown_scenario_raises_key_error,
        test_missing_categories_degrade_confidence_not_crash,
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
