"""
OceanPulse AI — Task 4: Demo Scenarios tests.

Deliverable: Three deterministic scenarios matching the project contract.
Success criteria: Five consecutive runs of each scenario return the
required index and level.

The scenarios themselves were already built as part of Task 1's
demo_scenarios.py (calibrated ocean/fisheries/molecular inputs, all
labeled SourceStatus.DEMO). This file is Task 4's dedicated
verification surface for that existing logic — it does not change
demo_scenarios.py.

Run with:
    cd ml
    python -m pytest tests/test_demo_scenarios.py -v

or, without pytest installed:
    cd ml
    python tests/test_demo_scenarios.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fusion_engine.fusion import FusionEngine
from fusion_engine.schema import SourceStatus
from fusion_engine.demo_scenarios import SCENARIOS, get_scenario

RUNS_PER_SCENARIO = 5

EXPECTED = {
    "healthy_reef": (22, "STABLE"),
    "declining_fishery": (55, "WATCH"),
    "coral_bleaching": (88, "CRITICAL"),
}


# ---------------------------------------------------------------------
# Steps 1-3 / Success criteria: five consecutive runs of each scenario
# return the required index and level.
# ---------------------------------------------------------------------

def test_healthy_reef_five_consecutive_runs():
    engine = FusionEngine()
    expected_index, expected_level = EXPECTED["healthy_reef"]
    for i in range(RUNS_PER_SCENARIO):
        result = engine.analyze(get_scenario("healthy_reef"))
        assert result.index == expected_index, f"run {i+1}: index {result.index} != {expected_index}"
        assert result.level == expected_level, f"run {i+1}: level {result.level} != {expected_level}"
    print(f"OK healthy_reef: {RUNS_PER_SCENARIO}/{RUNS_PER_SCENARIO} runs "
          f"returned {expected_index}/{expected_level}")


def test_declining_fishery_five_consecutive_runs():
    engine = FusionEngine()
    expected_index, expected_level = EXPECTED["declining_fishery"]
    for i in range(RUNS_PER_SCENARIO):
        result = engine.analyze(get_scenario("declining_fishery"))
        assert result.index == expected_index, f"run {i+1}: index {result.index} != {expected_index}"
        assert result.level == expected_level, f"run {i+1}: level {result.level} != {expected_level}"
    print(f"OK declining_fishery: {RUNS_PER_SCENARIO}/{RUNS_PER_SCENARIO} runs "
          f"returned {expected_index}/{expected_level}")


def test_coral_bleaching_five_consecutive_runs():
    engine = FusionEngine()
    expected_index, expected_level = EXPECTED["coral_bleaching"]
    for i in range(RUNS_PER_SCENARIO):
        result = engine.analyze(get_scenario("coral_bleaching"))
        assert result.index == expected_index, f"run {i+1}: index {result.index} != {expected_index}"
        assert result.level == expected_level, f"run {i+1}: level {result.level} != {expected_level}"
    print(f"OK coral_bleaching: {RUNS_PER_SCENARIO}/{RUNS_PER_SCENARIO} runs "
          f"returned {expected_index}/{expected_level}")


# ---------------------------------------------------------------------
# Step 4: ocean, fisheries, and molecular signals are attached to each
# scenario (all three categories present, not just some).
# ---------------------------------------------------------------------

def test_every_scenario_has_all_three_signal_categories_attached():
    for name, fusion_input in SCENARIOS.items():
        assert fusion_input.ocean is not None, f"{name} missing ocean signal"
        assert fusion_input.fisheries is not None, f"{name} missing fisheries signal"
        assert fusion_input.molecular is not None, f"{name} missing molecular signal"
    print("OK all three scenarios have ocean, fisheries, and molecular "
          "signals attached")


# ---------------------------------------------------------------------
# Step 5: simulated source fields are labeled DEMO.
# ---------------------------------------------------------------------

def test_every_scenario_signal_source_is_labeled_demo():
    for name, fusion_input in SCENARIOS.items():
        assert fusion_input.ocean.source == SourceStatus.DEMO, (
            f"{name} ocean source is not DEMO: {fusion_input.ocean.source}"
        )
        assert fusion_input.fisheries.source == SourceStatus.DEMO, (
            f"{name} fisheries source is not DEMO: {fusion_input.fisheries.source}"
        )
        assert fusion_input.molecular.source == SourceStatus.DEMO, (
            f"{name} molecular source is not DEMO: {fusion_input.molecular.source}"
        )
    print("OK all three scenarios label ocean/fisheries/molecular "
          "source fields as DEMO")


def test_analysis_result_sources_report_demo():
    """The FusionResult.sources dict (the one that reaches the API
    response) must also report DEMO for every category, not just the
    input schema."""
    engine = FusionEngine()
    for name, fusion_input in SCENARIOS.items():
        result = engine.analyze(fusion_input)
        assert result.sources == {
            "ocean": "DEMO", "fisheries": "DEMO", "molecular": "DEMO",
        }, f"{name} result.sources incorrect: {result.sources}"
    print("OK all three scenarios' FusionResult.sources report DEMO "
          "for every category")


if __name__ == "__main__":
    tests = [
        test_healthy_reef_five_consecutive_runs,
        test_declining_fishery_five_consecutive_runs,
        test_coral_bleaching_five_consecutive_runs,
        test_every_scenario_has_all_three_signal_categories_attached,
        test_every_scenario_signal_source_is_labeled_demo,
        test_analysis_result_sources_report_demo,
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
