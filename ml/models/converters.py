"""
OceanPulse AI — ML Models
Task 1: ML Input/Output Schema — validation and conversion.

Converts already-normalized fusion_engine.schema features into the
exact ordered numeric vectors XGBOOST_FEATURE_SPECS and
ISOLATION_FOREST_FEATURE_SPECS define, raising a clear error if a
value is missing, the wrong type, or outside its documented range.

This is deliberately separate from fusion_engine/ — the Fusion Engine
must keep working with zero ML dependencies (CLAUDE.md: "the engine
works without ML"), so nothing in fusion_engine/ imports from here.
The direction of the dependency is one-way: ml/models/ -> fusion_engine/schema.
"""

from typing import Dict, List

from fusion_engine.schema import FisheriesFeatures, MolecularFeatures, OceanFeatures
from .schema import (
    FeatureSpec,
    ISOLATION_FOREST_FEATURE_SPECS,
    XGBOOST_FEATURE_SPECS,
)


class FeatureValidationError(ValueError):
    """Raised when a normalized input value fails schema validation."""


def _validate_and_cast(spec: FeatureSpec, value) -> float:
    if value is None:
        raise FeatureValidationError(
            f"'{spec.name}' (source: {spec.source}) is missing/None."
        )
    try:
        cast_value = float(value)
    except (TypeError, ValueError) as exc:
        raise FeatureValidationError(
            f"'{spec.name}' (source: {spec.source}) is not numeric: {value!r}"
        ) from exc

    if not (spec.min_value <= cast_value <= spec.max_value):
        raise FeatureValidationError(
            f"'{spec.name}' (source: {spec.source}) value {cast_value} is "
            f"outside the expected range [{spec.min_value}, {spec.max_value}]."
        )
    return cast_value


def _species_richness_delta_pct(molecular: MolecularFeatures) -> float:
    """
    Derived feature: % decline in species richness vs. baseline.
    Not a new Data-layer field — computed purely from
    MolecularFeatures.species_richness and .baseline_richness, both of
    which already exist in fusion_engine/schema.py.
    """
    if molecular.baseline_richness <= 0:
        return 0.0
    return ((molecular.baseline_richness - molecular.species_richness)
             / molecular.baseline_richness) * 100.0


def to_xgboost_input(fisheries: FisheriesFeatures) -> Dict[str, float]:
    """
    Validate and convert normalized FisheriesFeatures into the
    fisheries stock / CPUE trend XGBoost model's input format.

    Returns an ordered dict (insertion order == XGBOOST_FEATURE_SPECS
    order) so callers can do `list(result.values())` for a plain
    feature vector once the model is wired in.

    Raises FeatureValidationError if any value is missing, non-numeric,
    or out of range.
    """
    if fisheries is None:
        raise FeatureValidationError(
            "fisheries input is required for the XGBoost stock/CPUE model."
        )

    raw_values = {
        "cpue_trend_pct": fisheries.cpue_trend_pct,
        "vessel_density_index": fisheries.vessel_density_index,
    }
    return {
        spec.name: _validate_and_cast(spec, raw_values[spec.name])
        for spec in XGBOOST_FEATURE_SPECS
    }


def to_isolation_forest_input(
    ocean: OceanFeatures,
    fisheries: FisheriesFeatures,
    molecular: MolecularFeatures,
) -> Dict[str, float]:
    """
    Validate and convert normalized ocean/fisheries/molecular features
    into the ecosystem anomaly IsolationForest model's input format.

    All three signal groups are required — ecosystem-wide anomaly
    detection needs the full picture. (Contrast with the Fusion
    Engine's rule-based scoring, which degrades gracefully with partial
    data; that graceful-degradation behavior is unchanged and lives
    entirely in fusion_engine/, not here.)

    Raises FeatureValidationError if any value is missing, non-numeric,
    or out of range.
    """
    missing = [
        name for name, value in
        (("ocean", ocean), ("fisheries", fisheries), ("molecular", molecular))
        if value is None
    ]
    if missing:
        raise FeatureValidationError(
            f"IsolationForest model requires all three signal groups; "
            f"missing: {', '.join(missing)}."
        )

    raw_values = {
        "sst_anomaly_c": ocean.sst_anomaly_c,
        "chlorophyll_a_anomaly_pct": ocean.chlorophyll_a_anomaly_pct,
        "salinity_anomaly_psu": ocean.salinity_anomaly_psu,
        "cpue_trend_pct": fisheries.cpue_trend_pct,
        "vessel_density_index": fisheries.vessel_density_index,
        "species_richness_delta_pct": _species_richness_delta_pct(molecular),
    }
    return {
        spec.name: _validate_and_cast(spec, raw_values[spec.name])
        for spec in ISOLATION_FOREST_FEATURE_SPECS
    }


def xgboost_feature_vector(converted: Dict[str, float]) -> List[float]:
    """Ordered list form of an already-converted XGBoost input dict."""
    return [converted[spec.name] for spec in XGBOOST_FEATURE_SPECS]


def isolation_forest_feature_vector(converted: Dict[str, float]) -> List[float]:
    """Ordered list form of an already-converted IsolationForest input dict."""
    return [converted[spec.name] for spec in ISOLATION_FOREST_FEATURE_SPECS]
