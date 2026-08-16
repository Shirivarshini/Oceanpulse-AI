from ml.fusion_engine.demo_scenarios import get_scenario
from ml.fusion_engine.schema import FusionResult, SourceStatus
from ml.models.ml_fusion_engine import MLEnhancedFusionEngine

from .data_adapter import resolve_demo_sources


# The ML-enhanced engine wraps the existing rule-based FusionEngine.
# When trained ML artifacts are unavailable, it automatically falls
# back to the rule-based engine without changing the result.
_ENGINE = MLEnhancedFusionEngine()


def run_demo_fusion(scenario: str) -> FusionResult:
    """
    Resolve the actual Data source first, then run the canonical
    calibrated DEMO FusionInput through the ML-enhanced Fusion Engine.

    Responsibilities:
        Data Fallback -> selects LIVE/CACHED/HISTORICAL/DEMO
        Backend       -> attaches resolved source metadata
        ML Engine     -> performs rule-based fusion and optional ML enhancement

    The ML layer never owns source selection. Source status is resolved
    by the Data Fallback package and passed into the normalized
    FusionInput before analysis.

    When no trained ML models are available, MLEnhancedFusionEngine
    returns the original rule-based FusionResult unchanged.
    """
    # 1. Resolve the actual source tier for every data category.
    #    Data Fallback owns:
    #        LIVE -> CACHED -> HISTORICAL -> DEMO
    resolved = resolve_demo_sources(scenario)

    # 2. Get the canonical normalized demo input.
    fusion_input = get_scenario(scenario)

    # 3. Attach the source selected by the Data Fallback layer.
    #
    #    IMPORTANT:
    #    ML must never decide whether a source is LIVE, CACHED,
    #    HISTORICAL, or DEMO.
    fusion_input.ocean.source = SourceStatus(
        resolved["sources"]["ocean"]
    )
    fusion_input.fisheries.source = SourceStatus(
        resolved["sources"]["fisheries"]
    )
    fusion_input.molecular.source = SourceStatus(
        resolved["sources"]["molecular"]
    )

    # 4. Run the ML-enhanced engine.
    #
    #    If trained models are unavailable, this is equivalent to:
    #
    #        FusionEngine().analyze(fusion_input)
    #
    #    If trained models become available later, the ML layer
    #    automatically adds its explainable factors/confidence
    #    contribution without requiring another Backend change.
    return _ENGINE.analyze(fusion_input)