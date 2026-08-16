"""
OceanPulse AI — Task 2: Index Classification tests.

Deliverable: Index-level and confidence logic.
Success criteria: Boundary tests for 29, 30, 59, 60, 79, and 80 return
the specified levels.

The classification logic itself (LEVEL_BANDS / index_to_level) and the
confidence calculation (FusionEngine._confidence) were already built as
part of Task 1's engine.py, since the index and its level are computed
together in one pass. This file is Task 2's dedicated verification
surface for that existing logic — it does not change fusion.py.

Run with:
    cd ml
    python -m pytest tests/test_index_classification.py -v

or, without pytest installed:
    cd ml
    python tests/test_index_classification.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fusion_engine.fusion import FusionEngine, index_to_level
from fusion_engine.schema import (
    FusionInput, OceanFeatures, FisheriesFeatures, MolecularFeatures,
    SourceStatus,
)


# ---------------------------------------------------------------------
# Step 1-4 / Success criteria: the six required boundary tests.
# ---------------------------------------------------------------------

def test_boundary_29_is_stable():
    assert index_to_level(29) == "STABLE"
    print("OK 29 -> STABLE")


def test_boundary_30_is_watch():
    assert index_to_level(30) == "WATCH"
    print("OK 30 -> WATCH")


def test_boundary_59_is_watch():
    assert index_to_level(59) == "WATCH"
    print("OK 59 -> WATCH")


def test_boundary_60_is_stressed():
    assert index_to_level(60) == "STRESSED"
    print("OK 60 -> STRESSED")


def test_boundary_79_is_stressed():
    assert index_to_level(79) == "STRESSED"
    print("OK 79 -> STRESSED")


def test_boundary_80_is_critical():
    assert index_to_level(80) == "CRITICAL"
    print("OK 80 -> CRITICAL")


# ---------------------------------------------------------------------
# Extra edge coverage around the same boundaries (not the six required
# tests, but cheap insurance against off-by-one errors at the extremes).
# ---------------------------------------------------------------------

def test_boundary_0_is_stable():
    assert index_to_level(0) == "STABLE"


def test_boundary_100_is_critical():
    assert index_to_level(100) == "CRITICAL"


# ---------------------------------------------------------------------
# Step 5: confidence is calculated from available signal inputs.
# ---------------------------------------------------------------------

def test_confidence_full_coverage_higher_than_partial():
    engine = FusionEngine()

    full = FusionInput(
        region_id="r1",
        ocean=OceanFeatures(sst_anomaly_c=0.5, source=SourceStatus.DEMO),
        fisheries=FisheriesFeatures(cpue_trend_pct=-10, source=SourceStatus.DEMO),
        molecular=MolecularFeatures(species_richness=90, baseline_richness=100,
                                     sample_quality=1.0, source=SourceStatus.DEMO),
    )
    ocean_only = FusionInput(
        region_id="r1",
        ocean=OceanFeatures(sst_anomaly_c=0.5, source=SourceStatus.DEMO),
        fisheries=None,
        molecular=None,
    )

    result_full = engine.analyze(full)
    result_partial = engine.analyze(ocean_only)

    assert result_full.confidence > result_partial.confidence
    print(f"OK full-coverage confidence ({result_full.confidence}) > "
          f"partial-coverage confidence ({result_partial.confidence})")


def test_confidence_low_sample_quality_lowers_confidence():
    engine = FusionEngine()

    base = FusionInput(
        region_id="r1",
        ocean=OceanFeatures(sst_anomaly_c=0.5, source=SourceStatus.DEMO),
        fisheries=FisheriesFeatures(cpue_trend_pct=-10, source=SourceStatus.DEMO),
        molecular=MolecularFeatures(species_richness=90, baseline_richness=100,
                                     sample_quality=1.0, source=SourceStatus.DEMO),
    )
    noisy_sample = FusionInput(
        region_id="r1",
        ocean=OceanFeatures(sst_anomaly_c=0.5, source=SourceStatus.DEMO),
        fisheries=FisheriesFeatures(cpue_trend_pct=-10, source=SourceStatus.DEMO),
        molecular=MolecularFeatures(species_richness=90, baseline_richness=100,
                                     sample_quality=0.3, source=SourceStatus.DEMO),
    )

    result_clean = engine.analyze(base)
    result_noisy = engine.analyze(noisy_sample)

    assert result_noisy.confidence < result_clean.confidence
    print(f"OK noisy-sample confidence ({result_noisy.confidence}) < "
          f"clean-sample confidence ({result_clean.confidence})")


def test_confidence_always_in_valid_range():
    engine = FusionEngine()
    fusion_input = FusionInput(region_id="r1", ocean=None, fisheries=None, molecular=None)
    result = engine.analyze(fusion_input)
    assert 0.0 <= result.confidence <= 1.0
    print(f"OK confidence in [0,1] even with zero signals: {result.confidence}")


# ---------------------------------------------------------------------
# Step 6: index, level, and confidence are returned together in the
# agreed schema (API_CONTRACT.md section 3 field names).
# ---------------------------------------------------------------------

def test_result_has_index_level_confidence_fields():
    engine = FusionEngine()
    fusion_input = FusionInput(
        region_id="r1",
        ocean=OceanFeatures(sst_anomaly_c=1.5, source=SourceStatus.DEMO),
        fisheries=FisheriesFeatures(cpue_trend_pct=-20, source=SourceStatus.DEMO),
        molecular=MolecularFeatures(species_richness=70, baseline_richness=100,
                                     sample_quality=0.9, source=SourceStatus.DEMO),
    )
    result = engine.analyze(fusion_input)

    assert hasattr(result, "index") and isinstance(result.index, int)
    assert hasattr(result, "level") and result.level in (
        "STABLE", "WATCH", "STRESSED", "CRITICAL"
    )
    assert hasattr(result, "confidence") and isinstance(result.confidence, float)
    assert result.level == index_to_level(result.index)
    print(f"OK schema fields present and level matches index: "
          f"index={result.index} level={result.level} confidence={result.confidence}")


if __name__ == "__main__":
    tests = [
        test_boundary_29_is_stable,
        test_boundary_30_is_watch,
        test_boundary_59_is_watch,
        test_boundary_60_is_stressed,
        test_boundary_79_is_stressed,
        test_boundary_80_is_critical,
        test_boundary_0_is_stable,
        test_boundary_100_is_critical,
        test_confidence_full_coverage_higher_than_partial,
        test_confidence_low_sample_quality_lowers_confidence,
        test_confidence_always_in_valid_range,
        test_result_has_index_level_confidence_fields,
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
