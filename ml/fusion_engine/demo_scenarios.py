"""
OceanPulse AI — Insight Fusion Engine
Predefined demo scenarios.

Per CLAUDE.md's ML fallback chain, "Demo scenario" is the last-resort
tier — a fixed, known-good input that keeps the product demoable even
if every upstream data source and model is unavailable. This module is
that tier for the three hackathon-required scenarios in
API_CONTRACT.md section 6:

    healthy_reef        -> 22 / STABLE   / NO_ALERT
    declining_fishery   -> 55 / WATCH    / NO_ALERT
    coral_bleaching     -> 88 / CRITICAL / ALERT_DISPATCHED   (primary judge demo)

IMPORTANT: The feature values below were deliberately calibrated (see
ml/tests/test_fusion_engine.py::test_demo_scenarios_match_contract) so
that running them through the SAME rule-based scoring pipeline used for
live/real regions reproduces exactly these index values. Nothing here
is hardcoded output — it is hardcoded, labeled-DEMO *input* that the
real engine computes over, per CLAUDE.md's "never fabricate ... model
metrics" rule. The Alert Gate decision itself (NO_ALERT / ALERT_DISPATCHED)
is owned by the Backend, not this module — see API_CONTRACT.md section 12.
"""

from .schema import (
    FusionInput,
    OceanFeatures,
    FisheriesFeatures,
    MolecularFeatures,
    SourceStatus,
)

_DEMO_REGION = {
    "id": "gulf-of-mannar",
    "name": "Gulf of Mannar",
    "latitude": 9.0,
    "longitude": 79.0,
}


def _scenario(region_id, sst, chla, cpue, vessel, rich, base, history=None):
    return FusionInput(
        region_id=region_id,
        ocean=OceanFeatures(
            sst_anomaly_c=sst,
            chlorophyll_a_anomaly_pct=chla,
            source=SourceStatus.DEMO,
        ),
        fisheries=FisheriesFeatures(
            cpue_trend_pct=cpue,
            vessel_density_index=vessel,
            source=SourceStatus.DEMO,
        ),
        molecular=MolecularFeatures(
            species_richness=rich,
            baseline_richness=base,
            rare_taxa_detected=0,
            invasive_taxa_detected=0,
            sample_quality=1.0,
            source=SourceStatus.DEMO,
        ),
        history=history or [],
    )


# Expected index: 22 -> STABLE -> NO_ALERT (threshold 70)
HEALTHY_REEF = _scenario(
    region_id=_DEMO_REGION["id"],
    sst=0.9, chla=0,
    cpue=-17, vessel=0.2,
    rich=15, base=20,
)

# Expected index: 55 -> WATCH -> NO_ALERT (threshold 70)
DECLINING_FISHERY = _scenario(
    region_id=_DEMO_REGION["id"],
    sst=1.14375, chla=0,
    cpue=-50, vessel=0.3,
    rich=50, base=100,
)

# Expected index: 88 -> CRITICAL -> ALERT_DISPATCHED (threshold 70)
# Primary judge demo. History replays the 28 -> 55 -> 88 escalation
# from API_CONTRACT.md section 6 so the timeline chart shows the story,
# not just the final number.
CORAL_BLEACHING = _scenario(
    region_id=_DEMO_REGION["id"],
    sst=2.83125, chla=150,
    cpue=-45, vessel=1.0,
    rich=50, base=100,
    history=[
        {
            "timestamp": "2026-08-12T10:00:00Z",
            "index": 28,
            "event": "Baseline",
        },
        {
            "timestamp": "2026-08-13T10:00:00Z",
            "index": 55,
            "event": "Environmental stress increased",
        },
        # Final point's index is overwritten with the freshly-computed
        # value by FusionEngine._build_timeline if it doesn't already
        # match — kept here at 88 so the story reads correctly even if
        # someone edits the calibrated inputs above.
        {
            "timestamp": "2026-08-14T10:00:00Z",
            "index": 88,
            "event": "Critical threshold crossed",
        },
    ],
)

SCENARIOS = {
    "healthy_reef": HEALTHY_REEF,
    "declining_fishery": DECLINING_FISHERY,
    "coral_bleaching": CORAL_BLEACHING,
}


def get_scenario(name: str) -> FusionInput:
    """
    Raises KeyError for unknown scenario names — the Backend is
    responsible for catching that and returning the INVALID_SCENARIO
    error code per API_CONTRACT.md section 14.
    """
    return SCENARIOS[name]
