from fastapi import APIRouter, HTTPException

from ..schemas import SpeciesResponse


router = APIRouter(prefix="/api")


@router.get("/species/{id}", response_model=SpeciesResponse)
def get_species(id: str) -> SpeciesResponse:
    if id != "gulf-of-mannar":
        raise HTTPException(
            status_code=404,
            detail="Region not found",
        )

    return SpeciesResponse(
        region_id="gulf-of-mannar",
        species=[
            {
                "taxon": "Example species",
                "match_confidence": 0.94,
                "status": "common",
                "source": "DEMO",
            },
            {
                "taxon": "Example rare taxon",
                "match_confidence": 0.87,
                "status": "rare",
                "source": "DEMO",
            },
        ],
    )