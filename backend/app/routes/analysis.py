from copy import deepcopy
from fastapi import APIRouter

from ..alert_gate import evaluate_alert
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


def apply_alert_gate(analysis: AnalysisResponse) -> AnalysisResponse:
    result = deepcopy(analysis)

    decision = evaluate_alert(
        index=result.index,
        created_at=result.created_at,
        threshold=result.alert.threshold,
    )

    result.alert.status = decision.status
    result.alert.threshold = decision.threshold
    result.alert.reason = decision.reason

    return result

@router.post("/demo/analyze", response_model=AnalysisResponse)
def demo_analyze(request: DemoAnalyzeRequest) -> AnalysisResponse:
    scenarios = {
        "healthy_reef": HEALTHY_ANALYSIS,
        "declining_fishery": DECLINING_ANALYSIS,
        "coral_bleaching": CORAL_ANALYSIS,
    }

    return apply_alert_gate(scenarios[request.scenario])


@router.post("/analyze", response_model=AnalysisResponse)
def analyze(request: AnalyzeRequest) -> AnalysisResponse:
    return apply_alert_gate(CORAL_ANALYSIS)