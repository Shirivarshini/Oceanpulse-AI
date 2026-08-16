from fastapi import APIRouter, HTTPException

from ..schemas import RegionResponse


router = APIRouter(prefix="/api")


@router.get("/region/{id}", response_model=RegionResponse)
def get_region(id: str) -> RegionResponse:
    if id != "gulf-of-mannar":
        raise HTTPException(
            status_code=404,
            detail="Region not found",
        )

    return RegionResponse(
        id="gulf-of-mannar",
        name="Gulf of Mannar",
        latitude=9.0,
        longitude=79.0,
        bounding_box={
            "min_lat": 8.5,
            "max_lat": 9.5,
            "min_lon": 78.5,
            "max_lon": 79.5,
        },
        source="DEMO",
    )