from ml.fusion_engine import FusionEngine
from ml.fusion_engine.demo_scenarios import get_scenario
from ml.fusion_engine.schema import FusionResult, SourceStatus

from .data_adapter import resolve_demo_sources


_ENGINE = FusionEngine()


def run_demo_fusion(scenario: str) -> FusionResult:
    """
    Resolve the actual Data source first, then run the canonical
    calibrated DEMO FusionInput through the Fusion Engine.

    The Data Fallback package owns source selection.
    The Fusion Engine owns scoring.
    """
    resolved = resolve_demo_sources(scenario)

    fusion_input = get_scenario(scenario)

    fusion_input.ocean.source = SourceStatus(resolved["sources"]["ocean"])
    fusion_input.fisheries.source = SourceStatus(resolved["sources"]["fisheries"])
    fusion_input.molecular.source = SourceStatus(resolved["sources"]["molecular"])

    return _ENGINE.analyze(fusion_input)
