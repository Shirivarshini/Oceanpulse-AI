"""
OceanPulse AI — ML Models
Task 1: ML Input/Output Schema.

This module defines the stable internal schema between the Fusion
Engine's already-normalized features (fusion_engine/schema.py, owned by
the Data layer / Task 1 of the Fusion Engine plan) and the two Phase-5
models named in CLAUDE.md's tech stack:

    - XGBoost        -> fisheries stock / CPUE trend classification
    - IsolationForest -> ecosystem anomaly detection

Rules this module follows (per the task card):
  - Only OceanFeatures / FisheriesFeatures / MolecularFeatures fields
    that already exist in fusion_engine/schema.py are used as model
    inputs. No new fields are invented or requested from the Data
    layer here.
  - Every feature has an explicit name, numeric type, and expected
    range, so a bad/out-of-domain value is caught before it reaches a
    model rather than silently producing a bad prediction.
  - This module does NOT change API_CONTRACT.md. It is purely an
    internal ML-layer schema; nothing here is exposed to the Backend
    or Frontend directly.
  - This task defines the schema and validates/converts against it.
    It does NOT train or run either model — that's the next Phase 5
    task ("Add XGBoost interface" / "Add IsolationForest interface").
    `available=False` on both output dataclasses reflects that no
    model is wired in yet; CLAUDE.md's rule "never claim something is
    trained ... unless it actually is" applies here.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------
# Feature specs — traceable to the exact source field on the Data
# layer's normalized schema, with explicit dtype and valid range.
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class FeatureSpec:
    name: str
    dtype: type              # float or int
    min_value: float
    max_value: float
    source: str                # e.g. "FisheriesFeatures.cpue_trend_pct"
    description: str


# --- XGBoost: fisheries stock / CPUE trend classification ------------
# Scoped to the fisheries signal group only, matching what CLAUDE.md
# names this model for. Feature order is significant — converters.py
# preserves it when building the model input vector.
XGBOOST_FEATURE_SPECS = (
    FeatureSpec(
        name="cpue_trend_pct",
        dtype=float,
        min_value=-100.0,
        max_value=100.0,
        source="FisheriesFeatures.cpue_trend_pct",
        description="% change in catch-per-unit-effort. Negative = decline.",
    ),
    FeatureSpec(
        name="vessel_density_index",
        dtype=float,
        min_value=0.0,
        max_value=1.0,
        source="FisheriesFeatures.vessel_density_index",
        description="Normalized AIS vessel-density pressure, 0.0-1.0.",
    ),
)

# --- IsolationForest: ecosystem anomaly detection ---------------------
# Ecosystem-wide anomaly detection draws on all three signal groups,
# since an anomaly can show up as an unusual combination across ocean,
# fisheries, and molecular signals even if no single one is extreme.
# `species_richness_delta_pct` is a derived value (computed purely from
# two existing MolecularFeatures fields — not a new field requested
# from the Data layer; see converters.py).
ISOLATION_FOREST_FEATURE_SPECS = (
    FeatureSpec(
        name="sst_anomaly_c",
        dtype=float,
        min_value=-5.0,
        max_value=10.0,
        source="OceanFeatures.sst_anomaly_c",
        description="Sea-surface temperature anomaly, degrees C above baseline.",
    ),
    FeatureSpec(
        name="chlorophyll_a_anomaly_pct",
        dtype=float,
        min_value=-100.0,
        max_value=500.0,
        source="OceanFeatures.chlorophyll_a_anomaly_pct",
        description="% deviation from baseline chlorophyll-a (HAB proxy).",
    ),
    FeatureSpec(
        name="salinity_anomaly_psu",
        dtype=float,
        min_value=-10.0,
        max_value=10.0,
        source="OceanFeatures.salinity_anomaly_psu",
        description="Salinity anomaly, practical salinity units.",
    ),
    FeatureSpec(
        name="cpue_trend_pct",
        dtype=float,
        min_value=-100.0,
        max_value=100.0,
        source="FisheriesFeatures.cpue_trend_pct",
        description="% change in catch-per-unit-effort. Negative = decline.",
    ),
    FeatureSpec(
        name="vessel_density_index",
        dtype=float,
        min_value=0.0,
        max_value=1.0,
        source="FisheriesFeatures.vessel_density_index",
        description="Normalized AIS vessel-density pressure, 0.0-1.0.",
    ),
    FeatureSpec(
        name="species_richness_delta_pct",
        dtype=float,
        min_value=-100.0,
        max_value=100.0,
        source=("derived: (MolecularFeatures.baseline_richness - "
                 "MolecularFeatures.species_richness) / baseline_richness * 100"),
        description="% decline in observed species richness vs. baseline. "
                     "0.0 when baseline_richness is 0 (no baseline to compare).",
    ),
)


# ---------------------------------------------------------------------
# Output schema
# ---------------------------------------------------------------------

class StockTrendClass(str, Enum):
    """
    Provisional class labels for the XGBoost fisheries stock / CPUE
    trend classifier. Final label set is subject to review once the
    model is actually trained (next Phase 5 task) — this task only
    reserves the schema shape.
    """
    STABLE = "stable"
    DECLINING = "declining"
    CRITICAL_DECLINE = "critical_decline"


@dataclass
class XGBoostOutput:
    """
    Output shape for the fisheries stock / CPUE trend classifier.

    `available=False` means no trained model is wired in yet — callers
    (the Fusion Engine's ML-fallback tier) must treat this as "model
    unavailable" and fall back to rule-based scoring, per CLAUDE.md's
    ML fallback chain. This dataclass exists so that fallback check has
    a stable shape to check against once the model IS wired in.
    """
    stock_trend_class: Optional[StockTrendClass] = None
    confidence: Optional[float] = None   # 0.0-1.0
    model_version: Optional[str] = None
    available: bool = False


@dataclass
class IsolationForestOutput:
    """
    Output shape for the ecosystem anomaly detector.

    `anomaly_score` follows scikit-learn's IsolationForest convention
    of higher = more normal, lower/negative = more anomalous, but is
    re-expressed here as `normalized_anomaly_score` in 0.0-1.0 (higher
    = more anomalous) so downstream consumers don't need to know the
    sklearn sign convention.

    `available=False` means no trained model is wired in yet — same
    fallback rule as XGBoostOutput above.
    """
    normalized_anomaly_score: Optional[float] = None  # 0.0 (normal) - 1.0 (anomalous)
    is_anomaly: Optional[bool] = None
    model_version: Optional[str] = None
    available: bool = False
