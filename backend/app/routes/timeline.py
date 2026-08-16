from fastapi import APIRouter, HTTPException

from ..demo_data import CORAL_ANALYSIS
from ..schemas import TimelineResponse


router = APIRouter(prefix="/api")


@router.get("/timeline/{id}", response_model=TimelineResponse)
def get_timeline(id: str) -> TimelineResponse:
    if id != CORAL_ANALYSIS.analysis_id:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    return TimelineResponse(
        analysis_id=CORAL_ANALYSIS.analysis_id,
        timeline=CORAL_ANALYSIS.timeline,
        source="DEMO",
    )