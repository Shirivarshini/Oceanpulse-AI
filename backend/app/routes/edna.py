from fastapi import APIRouter, HTTPException

from ..schemas import EDNAResponse


router = APIRouter(prefix="/api")


@router.get("/edna/matches/{sample_id}", response_model=EDNAResponse)
def get_edna_matches(sample_id: str) -> EDNAResponse:
    if sample_id != "sample-001":
        raise HTTPException(
            status_code=404,
            detail="Sample not found",
        )

    return EDNAResponse(
        sample_id="sample-001",
        species_richness=17,
        matches=[
            {
                "taxon": "Example species",
                "confidence": 0.96,
                "status": "common",
            },
            {
                "taxon": "Example rare taxon",
                "confidence": 0.82,
                "status": "rare",
            },
        ],
        flags=[],
        source="DEMO",
    )