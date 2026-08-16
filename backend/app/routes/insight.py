from fastapi import APIRouter, HTTPException

from ..demo_data import CORAL_ANALYSIS
from ..schemas import AnalysisResponse


router = APIRouter(prefix="/api")


@router.get("/insight/{id}", response_model=AnalysisResponse)
def get_insight(id: str) -> AnalysisResponse:
    if id != CORAL_ANALYSIS.analysis_id:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found",
        )

    return CORAL_ANALYSIS