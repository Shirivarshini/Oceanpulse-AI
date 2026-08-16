from ml.fusion_engine import FusionEngine
from ml.fusion_engine.demo_scenarios import get_scenario
from ml.fusion_engine.schema import FusionResult


_ENGINE = FusionEngine()


def run_demo_fusion(scenario: str) -> FusionResult:
    fusion_input = get_scenario(scenario)
    return _ENGINE.analyze(fusion_input)