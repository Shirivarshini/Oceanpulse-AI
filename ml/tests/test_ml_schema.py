"""
OceanPulse AI — ML Models
Task 1: ML Input/Output Schema tests.

Done when: a sample normalized input can be validated and converted
into the ML model input format.

Run with:
    cd ml
    python -m pytest tests/test_ml_schema.py -v

or, without pytest installed:
    cd ml
    python tests/test_ml_schema.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fusion_engine.schema import OceanFeatures, FisheriesFeatures, MolecularFeatures
from models.schema import XGBOOST_FEATURE_SPECS, ISOLATION_FOREST_FEATURE_SPECS
from models.converters import (
    FeatureValidationError,
    to_xgboost_input,
    to_isolation_forest_input,
    xgboost_feature_vector,
    isolation_forest_feature_vector,
)


def _sample_ocean():
    return OceanFeatures(sst_anomaly_c=1.5, chlorophyll_a_anomaly_pct=60,
                          salinity_anomaly_psu=-0.5)


def _sample_fisheries():
    return FisheriesFeatures(cpue_trend_pct=-30, vessel_density_index=0.7)


def _sample_molecular():
    return MolecularFeatures(species_richness=60, baseline_richness=100)


# ---------------------------------------------------------------------
# "Done when" criteria: a sample normalized input validates and
# converts into the ML model input format.
# ---------------------------------------------------------------------

def test_sample_fisheries_input_converts_to_xgboost_format():
    converted = to_xgboost_input(_sample_fisheries())
    assert converted == {"cpue_trend_pct": -30.0, "vessel_density_index": 0.7}
    vector = xgboost_feature_vector(converted)
    assert vector == [-30.0, 0.7]
    print(f"OK XGBoost conversion: {converted} -> vector {vector}")


def test_sample_multi_domain_input_converts_to_isolation_forest_format():
    converted = to_isolation_forest_input(
        _sample_ocean(), _sample_fisheries(), _sample_molecular()
    )
    expected = {
        "sst_anomaly_c": 1.5,
        "chlorophyll_a_anomaly_pct": 60.0,
        "salinity_anomaly_psu": -0.5,
        "cpue_trend_pct": -30.0,
        "vessel_density_index": 0.7,
        "species_richness_delta_pct": 40.0,  # (100-60)/100*100
    }
    assert converted == expected
    vector = isolation_forest_feature_vector(converted)
    assert len(vector) == len(ISOLATION_FOREST_FEATURE_SPECS)
    print(f"OK IsolationForest conversion: {converted} -> vector {vector}")


# ---------------------------------------------------------------------
# Step 1/2: exact feature names and ranges/types are enforced.
# ---------------------------------------------------------------------

def test_xgboost_feature_names_and_order_match_spec():
    names = [spec.name for spec in XGBOOST_FEATURE_SPECS]
    assert names == ["cpue_trend_pct", "vessel_density_index"]


def test_isolation_forest_feature_names_and_order_match_spec():
    names = [spec.name for spec in ISOLATION_FOREST_FEATURE_SPECS]
    assert names == [
        "sst_anomaly_c",
        "chlorophyll_a_anomaly_pct",
        "salinity_anomaly_psu",
        "cpue_trend_pct",
        "vessel_density_index",
        "species_richness_delta_pct",
    ]


def test_out_of_range_value_is_rejected():
    bad_fisheries = FisheriesFeatures(cpue_trend_pct=-30, vessel_density_index=5.0)
    try:
        to_xgboost_input(bad_fisheries)
        assert False, "expected FeatureValidationError for out-of-range value"
    except FeatureValidationError as e:
        print(f"OK out-of-range value rejected: {e}")


def test_non_numeric_value_is_rejected():
    bad_ocean = OceanFeatures(sst_anomaly_c="warm", chlorophyll_a_anomaly_pct=10)
    try:
        to_isolation_forest_input(bad_ocean, _sample_fisheries(), _sample_molecular())
        assert False, "expected FeatureValidationError for non-numeric value"
    except FeatureValidationError as e:
        print(f"OK non-numeric value rejected: {e}")


def test_missing_signal_group_is_rejected_for_isolation_forest():
    try:
        to_isolation_forest_input(None, _sample_fisheries(), _sample_molecular())
        assert False, "expected FeatureValidationError for missing ocean signal"
    except FeatureValidationError as e:
        print(f"OK missing signal group rejected: {e}")


def test_missing_fisheries_is_rejected_for_xgboost():
    try:
        to_xgboost_input(None)
        assert False, "expected FeatureValidationError for missing fisheries"
    except FeatureValidationError as e:
        print(f"OK missing fisheries input rejected: {e}")


# ---------------------------------------------------------------------
# Derived feature edge case: no baseline richness to compare against.
# ---------------------------------------------------------------------

def test_zero_baseline_richness_yields_zero_delta_not_a_crash():
    molecular = MolecularFeatures(species_richness=10, baseline_richness=0)
    converted = to_isolation_forest_input(
        _sample_ocean(), _sample_fisheries(), molecular
    )
    assert converted["species_richness_delta_pct"] == 0.0
    print("OK zero baseline_richness yields a 0.0 delta instead of dividing by zero")


# ---------------------------------------------------------------------
# No new fields invented — every feature spec traces back to an
# existing fusion_engine.schema field (or a documented derivation of
# two existing fields).
# ---------------------------------------------------------------------

def test_every_feature_spec_traces_to_an_existing_data_layer_field():
    known_fields = {
        "OceanFeatures.sst_anomaly_c",
        "OceanFeatures.chlorophyll_a_anomaly_pct",
        "OceanFeatures.salinity_anomaly_psu",
        "FisheriesFeatures.cpue_trend_pct",
        "FisheriesFeatures.vessel_density_index",
    }
    for spec in list(XGBOOST_FEATURE_SPECS) + list(ISOLATION_FOREST_FEATURE_SPECS):
        is_known_field = spec.source in known_fields
        is_documented_derivation = spec.source.startswith("derived:")
        assert is_known_field or is_documented_derivation, (
            f"'{spec.name}' source '{spec.source}' is neither an existing "
            "Data-layer field nor a documented derivation."
        )
    print("OK every ML feature traces to an existing normalized Data-layer "
          "field or a documented derivation of existing fields")


if __name__ == "__main__":
    tests = [
        test_sample_fisheries_input_converts_to_xgboost_format,
        test_sample_multi_domain_input_converts_to_isolation_forest_format,
        test_xgboost_feature_names_and_order_match_spec,
        test_isolation_forest_feature_names_and_order_match_spec,
        test_out_of_range_value_is_rejected,
        test_non_numeric_value_is_rejected,
        test_missing_signal_group_is_rejected_for_isolation_forest,
        test_missing_fisheries_is_rejected_for_xgboost,
        test_zero_baseline_richness_yields_zero_delta_not_a_crash,
        test_every_feature_spec_traces_to_an_existing_data_layer_field,
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
