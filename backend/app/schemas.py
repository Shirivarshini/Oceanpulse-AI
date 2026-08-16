from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


EcosystemLevel = Literal[
    "STABLE",
    "WATCH",
    "STRESSED",
    "CRITICAL",
]

AlertStatus = Literal[
    "NO_ALERT",
    "ALERT_DISPATCHED",
    "ALERT_BLOCKED_STALE",
]

SourceStatus = Literal[
    "LIVE",
    "CACHED",
    "HISTORICAL",
    "DEMO",
]

SpeciesStatus = Literal[
    "common",
    "rare",
    "invasive",
]


class DemoAnalyzeRequest(BaseModel):
    scenario: Literal[
        "healthy_reef",
        "declining_fishery",
        "coral_bleaching",
    ]


class AnalyzeRequest(BaseModel):
    region_id: str
    latitude: float
    longitude: float
    threshold: int = 70


class Region(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float


class Factor(BaseModel):
    name: str
    category: str
    impact: int
    severity: str
    description: str


class TimelineEvent(BaseModel):
    timestamp: datetime
    index: int
    event: str


class Alert(BaseModel):
    status: AlertStatus
    threshold: int
    reason: str


class Sources(BaseModel):
    ocean: SourceStatus
    fisheries: SourceStatus
    molecular: SourceStatus


class AnalysisResponse(BaseModel):
    analysis_id: str
    region: Region
    index: int = Field(ge=0, le=100)
    level: EcosystemLevel
    confidence: float = Field(ge=0, le=1)
    factors: list[Factor]
    timeline: list[TimelineEvent]
    alert: Alert
    sources: Sources
    created_at: datetime


class RegionResponse(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    bounding_box: dict[str, float]
    source: SourceStatus


class TimelineResponse(BaseModel):
    analysis_id: str
    timeline: list[TimelineEvent]
    source: SourceStatus


class SpeciesMatch(BaseModel):
    taxon: str
    match_confidence: float = Field(ge=0, le=1)
    status: SpeciesStatus
    source: SourceStatus


class SpeciesResponse(BaseModel):
    region_id: str
    species: list[SpeciesMatch]


class EDNAMatch(BaseModel):
    taxon: str
    confidence: float = Field(ge=0, le=1)
    status: SpeciesStatus


class EDNAResponse(BaseModel):
    sample_id: str
    species_richness: int
    matches: list[EDNAMatch]
    flags: list[str]
    source: SourceStatus