from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PIPELINE_DIR = PROJECT_ROOT / "data-pipeline"

if str(DATA_PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(DATA_PIPELINE_DIR))

from connectors import resolve_scenario_sources


def resolve_demo_sources(scenario: str) -> dict:
    """
    Resolve the actual source tier for each data category.

    The Data Fallback package owns:
        LIVE -> CACHED -> HISTORICAL -> DEMO

    This adapter only exposes its result to the Backend.
    """
    return resolve_scenario_sources(scenario)