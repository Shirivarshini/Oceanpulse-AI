"""
OceanPulse AI — Insight Fusion Engine
Normalized data schema.

These dataclasses define the contract between the Backend (which is
responsible for ingesting raw ocean/fisheries/molecular data and
normalizing it) and the Fusion Engine (which only ever consumes
already-normalized, unit-labeled features).

Per CLAUDE.md:
    The Fusion Engine is responsible for:
        feature processing, scoring, index calculation, confidence,
        explainability
    The Backend is responsible for:
        API validation, request handling, response formatting,
        Alert Gate, error handling

Nothing in this module talks to the network, a database, or the
filesystem. It is pure, deterministic, and side-effect free so the
same input always produces the same output (required by Task 1's
success criteria).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SourceStatus(str, Enum):
    """Per API_CONTRACT.md section 13 — allowed data-source values."""
    LIVE = "LIVE"
    CACHED = "CACHED"
    HISTORICAL = "HISTORICAL"
    DEMO = "DEMO"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class IndexLevel(str, Enum):
    """Per API_CONTRACT.md section 3 — index level bands."""
    STABLE = "STABLE"
    WATCH = "WATCH"
    STRESSED = "STRESSED"
    CRITICAL = "CRITICAL"


# ---------------------------------------------------------------------------
# Normalized category inputs
# ---------------------------------------------------------------------------
# All three feature groups are optional at the dataclass level because a
# region/sample may be missing one signal (e.g. no eDNA sample uploaded
# yet). The engine must degrade gracefully rather than fail — see
# fusion.py's confidence calculation and CLAUDE.md's "flag low-confidence
# or sparse-data regions" rule.

@dataclass
class OceanFeatures:
    """Normalized oceanographic signal for one region/time window."""
    sst_anomaly_c: float = 0.0          # Sea-surface temp anomaly, degrees C above baseline
    chlorophyll_a_anomaly_pct: float = 0.0  # % deviation from baseline chl-a (HAB proxy)
    salinity_anomaly_psu: float = 0.0   # Salinity anomaly, practical salinity units
    source: SourceStatus = SourceStatus.DEMO


@dataclass
class FisheriesFeatures:
    """Normalized fisheries-pressure signal for one region/time window."""
    cpue_trend_pct: float = 0.0         # % change in catch-per-unit-effort (negative = decline)
    vessel_density_index: float = 0.0   # 0.0-1.0 normalized AIS vessel-density pressure
    source: SourceStatus = SourceStatus.DEMO


@dataclass
class MolecularFeatures:
    """Normalized eDNA/metabarcoding signal for one region/sample."""
    species_richness: int = 0
    baseline_richness: int = 0
    rare_taxa_detected: int = 0
    invasive_taxa_detected: int = 0
    sample_quality: float = 1.0         # 0.0-1.0, lowers confidence when sparse/noisy
    source: SourceStatus = SourceStatus.DEMO


@dataclass
class FusionInput:
    """Everything the Fusion Engine needs for one analysis run."""
    region_id: str
    ocean: Optional[OceanFeatures] = None
    fisheries: Optional[FisheriesFeatures] = None
    molecular: Optional[MolecularFeatures] = None
    # Optional pre-baked timeline points for regions with a known
    # escalation history (used by demo scenarios; live regions may omit
    # this and let the engine emit a single-point timeline).
    history: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Output schema — mirrors API_CONTRACT.md section 3 field-for-field so the
# Backend can pass this straight into the response model without renaming
# anything.
# ---------------------------------------------------------------------------

@dataclass
class Factor:
    name: str
    category: str          # "ocean" | "fisheries" | "molecular"
    impact: int             # contribution to the 0-100 index
    severity: str            # "low" | "medium" | "high"
    description: str


@dataclass
class TimelinePoint:
    timestamp: str
    index: int
    event: str


@dataclass
class FusionResult:
    index: int
    level: str
    confidence: float
    factors: list
    timeline: list
    sources: dict
