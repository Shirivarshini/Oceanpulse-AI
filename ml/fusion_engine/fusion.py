"""
OceanPulse AI — Insight Fusion Engine (Task 1 deliverable)

Deterministic, rule-based core described in CLAUDE.md priority #1 and
implementation_plan.md Phase 4:

    "Create the deterministic core ecosystem-index pipeline ...
     The same input produces a stable, explainable index and the
     engine works without ML."

Public entry point: `FusionEngine.analyze(FusionInput) -> FusionResult`

This module contains NO network calls, NO database access, and NO
randomness. Every value in the output is a pure function of the input.
That is what makes the Member 3 verification step
(run twice, compare outputs) pass by construction.
"""

from datetime import datetime, timezone

from .schema import (
    FusionInput,
    FusionResult,
    OceanFeatures,
    FisheriesFeatures,
    MolecularFeatures,
    SourceStatus,
    TimelinePoint,
)
from . import scoring


# Index level bands — must match API_CONTRACT.md section 3 exactly.
LEVEL_BANDS = (
    (0, 29, "STABLE"),
    (30, 59, "WATCH"),
    (60, 79, "STRESSED"),
    (80, 100, "CRITICAL"),
)


def index_to_level(index: int) -> str:
    for lo, hi, name in LEVEL_BANDS:
        if lo <= index <= hi:
            return name
    # Defensive fallback — index is always clamped to 0-100 before this
    # is called, so this branch should be unreachable.
    return "CRITICAL" if index > 100 else "STABLE"


class FusionEngine:
    """
    Stateless. One instance can be reused (or a new one created) per
    request — it holds no mutable state between calls.
    """

    def analyze(self, fusion_input: FusionInput) -> FusionResult:
        ocean = fusion_input.ocean or OceanFeatures()
        fisheries = fusion_input.fisheries or FisheriesFeatures()
        molecular = fusion_input.molecular or MolecularFeatures()

        factors = []
        factors += scoring.score_ocean(ocean)
        factors += scoring.score_fisheries(fisheries)
        factors += scoring.score_molecular(molecular)

        # Sort by impact descending so the strongest driver of the index
        # is always first in the explainability panel.
        factors.sort(key=lambda f: f.impact, reverse=True)

        raw_index = sum(f.impact for f in factors)
        index = max(0, min(100, round(raw_index)))
        level = index_to_level(index)

        confidence = self._confidence(
            fusion_input, ocean, fisheries, molecular
        )

        sources = {
            "ocean": ocean.source.value if isinstance(ocean.source, SourceStatus) else ocean.source,
            "fisheries": fisheries.source.value if isinstance(fisheries.source, SourceStatus) else fisheries.source,
            "molecular": molecular.source.value if isinstance(molecular.source, SourceStatus) else molecular.source,
        }

        timeline = self._build_timeline(fusion_input, index)

        return FusionResult(
            index=index,
            level=level,
            confidence=confidence,
            factors=[f.__dict__ for f in factors],
            timeline=[t.__dict__ for t in timeline],
            sources=sources,
        )

    # -- internals ---------------------------------------------------

    def _confidence(
        self,
        fusion_input: FusionInput,
        ocean: OceanFeatures,
        fisheries: FisheriesFeatures,
        molecular: MolecularFeatures,
    ) -> float:
        """
        Confidence reflects data COMPLETENESS and QUALITY, not the size
        of the index. A region with all three signal types present and
        good eDNA sample quality gets high confidence even if the index
        itself is low (a confidently STABLE reading is still confident).

        Per CLAUDE.md: "Explicitly flag low-confidence or sparse-data
        regions in the UI rather than hiding the gap" — this is what
        drives that flag on the frontend.
        """
        weight_present = 0.0
        # Each category present contributes up to its share of 0.9;
        # the remaining 0.1 is a baseline so a fully-covered analysis
        # tops out at 1.0 and a single-signal analysis never reads 0.
        if fusion_input.ocean is not None:
            weight_present += 0.30
        if fusion_input.fisheries is not None:
            weight_present += 0.30
        if fusion_input.molecular is not None:
            weight_present += 0.30

        base = 0.10 + weight_present  # 0.10 - 1.00

        # eDNA sample quality directly discounts confidence, since a
        # noisy/sparse sample makes the molecular signal less trustworthy
        # even though data was technically "present".
        quality_penalty = 0.0
        if fusion_input.molecular is not None:
            quality_penalty = (1.0 - molecular.sample_quality) * 0.15

        confidence = max(0.30, min(0.98, base - quality_penalty))
        return round(confidence, 2)

    def _build_timeline(self, fusion_input: FusionInput, final_index: int):
        """
        If the caller supplied explicit history points (demo scenarios
        do this to show the 28 -> 55 -> 88 escalation from
        API_CONTRACT.md section 6), use them verbatim and append the
        final computed point if it isn't already the last entry.
        Otherwise emit a single-point timeline anchored to "now" —
        a live/first-time analysis has no history yet.
        """
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        if fusion_input.history:
            points = [
                TimelinePoint(
                    timestamp=p["timestamp"],
                    index=p["index"],
                    event=p["event"],
                )
                for p in fusion_input.history
            ]
            if not points or points[-1].index != final_index:
                points.append(TimelinePoint(
                    timestamp=now,
                    index=final_index,
                    event="Latest analysis",
                ))
            return points

        return [TimelinePoint(
            timestamp=now,
            index=final_index,
            event="Baseline",
        )]
