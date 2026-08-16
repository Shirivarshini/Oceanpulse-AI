"""
OceanPulse AI — Task 3: Explainability tests.

Deliverable: Factors and timeline explaining each analysis result.
Success criteria: Every demo analysis contains at least one factor and
timeline events that explain its index.

The explainability logic itself was already built as part of Task 1:
  - scoring.py assigns each factor a category, impact, severity, and a
    plain-language description (steps 1-5).
  - fusion.py's _build_timeline() generates timestamped timeline events
    for index changes (step 6).

This file is Task 3's dedicated verification surface for that existing
logic — it does not change scoring.py or fusion.py.

Run with:
    cd ml
    python -m pytest tests/test_explainability.py -v

or, without pytest installed:
    cd ml
    python tests/test_explainability.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fusion_engine.fusion import FusionEngine
from fusion_engine.schema import (
    FusionInput, OceanFeatures, FisheriesFeatures, MolecularFeatures,
    SourceStatus,
)
from fusion_engine.demo_scenarios import SCENARIOS

REQUIRED_FACTOR_FIELDS = {"name", "category", "impact", "severity", "description"}
REQUIRED_TIMELINE_FIELDS = {"timestamp", "index", "event"}
VALID_CATEGORIES = {"ocean", "fisheries", "molecular"}
VALID_SEVERITIES = {"low", "medium", "high"}


# ---------------------------------------------------------------------
# Success criteria: every demo scenario has >=1 factor and >=1 timeline
# event.
# ---------------------------------------------------------------------

def test_every_demo_scenario_has_at_least_one_factor():
    engine = FusionEngine()
    for name, fusion_input in SCENARIOS.items():
        result = engine.analyze(fusion_input)
        assert len(result.factors) >= 1, f"{name} produced zero factors"
        print(f"OK {name}: {len(result.factors)} factor(s)")


def test_every_demo_scenario_has_at_least_one_timeline_event():
    engine = FusionEngine()
    for name, fusion_input in SCENARIOS.items():
        result = engine.analyze(fusion_input)
        assert len(result.timeline) >= 1, f"{name} produced an empty timeline"
        print(f"OK {name}: {len(result.timeline)} timeline event(s)")


# ---------------------------------------------------------------------
# Steps 2-4: each factor has category, impact, severity.
# ---------------------------------------------------------------------

def test_every_factor_has_category_impact_severity():
    engine = FusionEngine()
    for name, fusion_input in SCENARIOS.items():
        result = engine.analyze(fusion_input)
        for factor in result.factors:
            assert REQUIRED_FACTOR_FIELDS.issubset(factor.keys()), (
                f"{name} factor missing fields: {factor}"
            )
            assert factor["category"] in VALID_CATEGORIES, (
                f"{name} factor has invalid category: {factor['category']}"
            )
            assert factor["severity"] in VALID_SEVERITIES, (
                f"{name} factor has invalid severity: {factor['severity']}"
            )
            assert isinstance(factor["impact"], int) and factor["impact"] > 0, (
                f"{name} factor has non-positive impact: {factor}"
            )
    print("OK every factor across all demo scenarios has a valid "
          "category, positive impact, and valid severity")


# ---------------------------------------------------------------------
# Step 5: each factor has a plain-language description.
# ---------------------------------------------------------------------

def test_every_factor_has_a_plain_language_description():
    engine = FusionEngine()
    for name, fusion_input in SCENARIOS.items():
        result = engine.analyze(fusion_input)
        for factor in result.factors:
            desc = factor["description"]
            assert isinstance(desc, str) and len(desc) >= 10, (
                f"{name} factor has missing/too-short description: {factor}"
            )
    print("OK every factor has a non-trivial description string")


def test_factor_descriptions_avoid_certainty_language():
    """
    Per CLAUDE.md: 'Never present outputs as a confirmed scientific or
    regulatory conclusion.' Descriptions should read as signals/patterns,
    not verdicts.
    """
    banned_phrases = ["confirmed", "proven", "guaranteed", "certainly is"]
    engine = FusionEngine()
    for name, fusion_input in SCENARIOS.items():
        result = engine.analyze(fusion_input)
        for factor in result.factors:
            desc_lower = factor["description"].lower()
            for phrase in banned_phrases:
                assert phrase not in desc_lower, (
                    f"{name} factor description uses certainty language "
                    f"('{phrase}'): {factor['description']}"
                )
    print("OK no factor description uses confirmed/proven/guaranteed language")


# ---------------------------------------------------------------------
# Step 6: timeline events are timestamped and describe index changes.
# ---------------------------------------------------------------------

def test_every_timeline_event_has_timestamp_index_event():
    engine = FusionEngine()
    for name, fusion_input in SCENARIOS.items():
        result = engine.analyze(fusion_input)
        for point in result.timeline:
            assert REQUIRED_TIMELINE_FIELDS.issubset(point.keys()), (
                f"{name} timeline point missing fields: {point}"
            )
            assert isinstance(point["timestamp"], str) and point["timestamp"], (
                f"{name} timeline point missing timestamp: {point}"
            )
            assert isinstance(point["index"], int), (
                f"{name} timeline point index is not an int: {point}"
            )
            assert isinstance(point["event"], str) and point["event"], (
                f"{name} timeline point missing event label: {point}"
            )
    print("OK every timeline event across all demo scenarios has a "
          "timestamp, index, and event label")


def test_coral_bleaching_timeline_final_point_matches_index():
    engine = FusionEngine()
    result = engine.analyze(SCENARIOS["coral_bleaching"])
    assert result.timeline[-1]["index"] == result.index, (
        "final timeline point should match the analysis's own index"
    )
    print(f"OK coral_bleaching timeline's final point ({result.timeline[-1]['index']}) "
          f"matches the analysis index ({result.index})")


# ---------------------------------------------------------------------
# Non-demo path: a live/custom analysis also produces explainability
# output, not just the three fixed demo scenarios.
# ---------------------------------------------------------------------

def test_custom_input_also_produces_factors_and_timeline():
    engine = FusionEngine()
    fusion_input = FusionInput(
        region_id="custom-region",
        ocean=OceanFeatures(sst_anomaly_c=1.2, source=SourceStatus.DEMO),
        fisheries=FisheriesFeatures(cpue_trend_pct=-25, source=SourceStatus.DEMO),
        molecular=MolecularFeatures(species_richness=60, baseline_richness=100,
                                     sample_quality=0.8, source=SourceStatus.DEMO),
    )
    result = engine.analyze(fusion_input)
    assert len(result.factors) >= 1
    assert len(result.timeline) >= 1
    print(f"OK custom input: {len(result.factors)} factor(s), "
          f"{len(result.timeline)} timeline event(s)")


if __name__ == "__main__":
    tests = [
        test_every_demo_scenario_has_at_least_one_factor,
        test_every_demo_scenario_has_at_least_one_timeline_event,
        test_every_factor_has_category_impact_severity,
        test_every_factor_has_a_plain_language_description,
        test_factor_descriptions_avoid_certainty_language,
        test_every_timeline_event_has_timestamp_index_event,
        test_coral_bleaching_timeline_final_point_matches_index,
        test_custom_input_also_produces_factors_and_timeline,
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
