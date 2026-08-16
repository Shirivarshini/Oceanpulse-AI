"""
OceanPulse AI — Insight Fusion Engine
Rule-based signal scoring.

Each function here converts ONE normalized feature group (ocean,
fisheries, or molecular) into a list of `Factor`s — a name, an impact
contribution (points toward the 0-100 index), a severity label, and a
plain-language description.

Design notes:
  - Every function is pure (no I/O, no randomness) so the same input
    always produces the same factors — required for Task 1's success
    criteria ("same input produces the same index on repeated
    executions").
  - Thresholds and weights are intentionally simple, linear, and
    documented inline. This is the MVP "rule-based scoring" tier from
    CLAUDE.md's ML fallback chain:
        1. Trained classifier/matcher   (ml/models.py, Phase 5)
        2. Similarity/heuristic match
        3. Rule-based scoring           <-- this module
        4. Demo scenario
  - Category impact caps (ocean 40, fisheries 35, molecular 25) sum to
    100 so a maximally-stressed region on every signal saturates at a
    CRITICAL index without needing an artificial clamp to feel right.
  - Language follows CLAUDE.md's rule to never present outputs as a
    confirmed conclusion (e.g. "signal suggests", "consistent with").
"""

from .schema import Factor, OceanFeatures, FisheriesFeatures, MolecularFeatures

# Category impact caps — must sum to 100.
OCEAN_CAP = 40
FISHERIES_CAP = 35
MOLECULAR_CAP = 25


def _severity(pct_of_cap: float) -> str:
    """Map how much of a factor's own cap was used to a severity label."""
    if pct_of_cap >= 0.66:
        return "high"
    if pct_of_cap >= 0.33:
        return "medium"
    return "low"


def score_ocean(f: OceanFeatures) -> list:
    """
    Ocean signal rules:
      - SST anomaly >= 0.3C is a detectable warming signal. Impact scales
        linearly from 0.3C (small) to 3.0C (extreme bleaching-risk range),
        capped at 32 of the 40-point ocean budget.
      - Chlorophyll-a anomaly >= 40% (positive) is treated as a possible
        harmful-algal-bloom (HAB) indicator, capped at 8 points.
    """
    factors = []

    if f.sst_anomaly_c >= 0.3:
        span = min(f.sst_anomaly_c, 3.0) - 0.3
        impact = round(min(32, (span / 2.7) * 32))
        if impact > 0:
            factors.append(Factor(
                name="Sea Surface Temperature Anomaly",
                category="ocean",
                impact=impact,
                severity=_severity(impact / 32),
                description=(
                    f"Sea surface temperature is {f.sst_anomaly_c:.1f}C above "
                    "baseline — a pattern consistent with elevated thermal stress."
                ),
            ))

    if f.chlorophyll_a_anomaly_pct >= 40:
        span = min(f.chlorophyll_a_anomaly_pct, 150) - 40
        impact = round(min(8, (span / 110) * 8))
        if impact > 0:
            factors.append(Factor(
                name="Harmful Algal Bloom Indicator",
                category="ocean",
                impact=impact,
                severity=_severity(impact / 8),
                description=(
                    f"Chlorophyll-a is {f.chlorophyll_a_anomaly_pct:.0f}% above "
                    "baseline, indicative of possible algal bloom activity."
                ),
            ))

    return factors


def score_fisheries(f: FisheriesFeatures) -> list:
    """
    Fisheries signal rules:
      - CPUE decline >= 5% is a detectable fishing-pressure signal. Impact
        scales linearly from 5% (small) to 50% (severe), capped at 27 of
        the 35-point fisheries budget.
      - Vessel density index >= 0.6 (of 0-1) is treated as a possible
        overfishing-pressure spike, capped at 8 points.
    """
    factors = []

    decline = -f.cpue_trend_pct  # negative trend => positive decline
    if decline >= 5:
        span = min(decline, 50) - 5
        impact = round(min(27, (span / 45) * 27))
        if impact > 0:
            factors.append(Factor(
                name="CPUE Decline",
                category="fisheries",
                impact=impact,
                severity=_severity(impact / 27),
                description=(
                    f"Catch-per-unit-effort shows a {decline:.0f}% declining "
                    "trend, indicative of possible stock depletion."
                ),
            ))

    if f.vessel_density_index >= 0.6:
        span = min(f.vessel_density_index, 1.0) - 0.6
        impact = round(min(8, (span / 0.4) * 8))
        if impact > 0:
            factors.append(Factor(
                name="Vessel Density Spike",
                category="fisheries",
                impact=impact,
                severity=_severity(impact / 8),
                description=(
                    "AIS-derived vessel density is elevated in this region, "
                    "a proxy for possible overfishing pressure."
                ),
            ))

    return factors


def score_molecular(f: MolecularFeatures) -> list:
    """
    Molecular / eDNA signal rules:
      - Species-richness decline (relative to baseline) >= 5% is a
        detectable biodiversity-loss signal. Impact scales linearly from
        5% to 50% decline, capped at 18 of the 25-point molecular budget.
      - Any invasive taxon detection adds a flat per-taxon impact
        (capped at 7 points) — invasive detections outrank rare-taxon
        flags since they carry higher ecological risk.
      - If no invasive taxa are found, rare-taxon detections add a
        smaller flat per-taxon impact (also capped at 7 points).

    Per API_CONTRACT.md / CLAUDE.md: eDNA matches are never presented as
    scientifically certain — description text always frames this as a
    molecular *signal*, not a confirmed finding.
    """
    factors = []

    if f.baseline_richness > 0:
        decline_pct = ((f.baseline_richness - f.species_richness)
                        / f.baseline_richness) * 100
        if decline_pct >= 5:
            span = min(decline_pct, 50) - 5
            impact = round(min(18, (span / 45) * 18))
            if impact > 0:
                factors.append(Factor(
                    name="Reduced Species Richness",
                    category="molecular",
                    impact=impact,
                    severity=_severity(impact / 18),
                    description=(
                        f"eDNA results show observed species richness down "
                        f"{decline_pct:.0f}% from baseline, a pattern "
                        "consistent with declining biodiversity."
                    ),
                ))

    if f.invasive_taxa_detected > 0:
        impact = round(min(7, 3 + (f.invasive_taxa_detected - 1) * 2))
        factors.append(Factor(
            name="Invasive Taxon Detected",
            category="molecular",
            impact=impact,
            severity="high",
            description=(
                f"Molecular signal suggests presence of "
                f"{f.invasive_taxa_detected} invasive taxon match(es) "
                "(see /api/edna/matches for per-taxon confidence)."
            ),
        ))
    elif f.rare_taxa_detected > 0:
        impact = round(min(7, 2 + (f.rare_taxa_detected - 1) * 1.5))
        factors.append(Factor(
            name="Rare Taxon Detected",
            category="molecular",
            impact=impact,
            severity="medium",
            description=(
                f"Molecular signal suggests presence of "
                f"{f.rare_taxa_detected} rare taxon match(es) "
                "(see /api/edna/matches for per-taxon confidence)."
            ),
        ))

    return factors
