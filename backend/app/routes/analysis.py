from fastapi import APIRouter

from ..demo_data import (
    CORAL_ANALYSIS,
    DECLINING_ANALYSIS,
    HEALTHY_ANALYSIS,
)
from ..schemas import (
    AnalysisResponse,
    AnalyzeRequest,
    DemoAnalyzeRequest,
)


router = APIRouter(prefix="/api")


@router.post("/demo/analyze", response_model=AnalysisResponse)
def demo_analyze(request: DemoAnalyzeRequest) -> AnalysisResponse:
    scenarios = {
        "healthy_reef": HEALTHY_ANALYSIS,
        "declining_fishery": DECLINING_ANALYSIS,
        "coral_bleaching": CORAL_ANALYSIS,
    }

    return scenarios[request.scenario]


@router.post("/analyze", response_model=AnalysisResponse)
def analyze(request: AnalyzeRequest) -> AnalysisResponse:
    return CORAL_ANALYSIS
