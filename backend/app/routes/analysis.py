from datetime import datetime, timezone

from fastapi import APIRouter

from ..alert_gate import evaluate_alert
from ..fusion_adapter import run_demo_fusion
from ..schemas import (
    Alert,
    AnalysisResponse,
    AnalyzeRequest,
    DemoAnalyzeRequest,
    Factor,
    Region,
    Sources,
    TimelineEvent,
)


router = APIRouter(prefix="/api")


def build_analysis_response(
    fusion_result,
    region: Region,
    threshold: int = 70,
) -> AnalysisResponse:
    created_at = datetime.now(timezone.utc)

    alert_decision = evaluate_alert(
        index=fusion_result.index,
        created_at=created_at,
        threshold=threshold,
    )

    return AnalysisResponse(
        analysis_id=f"analysis-{region.id}",
        region=region,
        index=fusion_result.index,
        level=fusion_result.level,
        confidence=fusion_result.confidence,
        factors=[
            Factor(**factor)
            for factor in fusion_result.factors
        ],
        timeline=[
            TimelineEvent(**event)
            for event in fusion_result.timeline
        ],
        alert=Alert(
            status=alert_decision.status,
            threshold=alert_decision.threshold,
            reason=alert_decision.reason,
        ),
        sources=Sources(**fusion_result.sources),
        created_at=created_at,
    )


@router.post("/demo/analyze", response_model=AnalysisResponse)
def demo_analyze(request: DemoAnalyzeRequest) -> AnalysisResponse:
    fusion_result = run_demo_fusion(request.scenario)

    region = Region(
        id="gulf-of-mannar",
        name="Gulf of Mannar",
        latitude=9.0,
        longitude=79.0,
    )

    return build_analysis_response(
        fusion_result=fusion_result,
        region=region,
        threshold=70,
    )


@router.post("/analyze", response_model=AnalysisResponse)
def analyze(request: AnalyzeRequest) -> AnalysisResponse:
    fusion_result = run_demo_fusion("coral_bleaching")

    region = Region(
        id=request.region_id,
        name="Gulf of Mannar",
        latitude=request.latitude,
        longitude=request.longitude,
    )

    return build_analysis_response(
        fusion_result=fusion_result,
        region=region,
        threshold=request.threshold,
    )
