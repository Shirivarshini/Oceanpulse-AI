from datetime import datetime, timezone

from .schemas import AnalysisResponse


REGION = {
    "id": "gulf-of-mannar",
    "name": "Gulf of Mannar",
    "latitude": 9.0,
    "longitude": 79.0,
}


def create_analysis(
    analysis_id: str,
    index: int,
    level: str,
    alert_status: str,
) -> AnalysisResponse:
    now = datetime.now(timezone.utc)

    return AnalysisResponse(
        analysis_id=analysis_id,
        region=REGION,
        index=index,
        level=level,
        confidence=0.91,
        factors=[
            {
                "name": "Sea Surface Temperature Anomaly",
                "category": "ocean",
                "impact": 31,
                "severity": "high",
                "description": "Elevated temperature signal detected.",
            },
            {
                "name": "CPUE Decline",
                "category": "fisheries",
                "impact": 22,
                "severity": "medium",
                "description": "Catch-per-unit-effort shows a declining trend.",
            },
            {
                "name": "Reduced Species Richness",
                "category": "molecular",
                "impact": 19,
                "severity": "high",
                "description": "eDNA results indicate reduced observed richness.",
            },
        ],
        timeline=[
            {
                "timestamp": datetime(
                    2026, 8, 12, 10, tzinfo=timezone.utc
                ),
                "index": 28,
                "event": "Baseline",
            },
            {
                "timestamp": datetime(
                    2026, 8, 13, 10, tzinfo=timezone.utc
                ),
                "index": 55,
                "event": "Environmental stress increased",
            },
            {
                "timestamp": datetime(
                    2026, 8, 14, 10, tzinfo=timezone.utc
                ),
                "index": index,
                "event": "Current analysis",
            },
        ],
        alert={
            "status": alert_status,
            "threshold": 70,
            "reason": (
                "Ecosystem index exceeded configured alert threshold."
                if alert_status == "ALERT_DISPATCHED"
                else "Ecosystem index is below configured alert threshold."
            ),
        },
        sources={
            "ocean": "DEMO",
            "fisheries": "DEMO",
            "molecular": "DEMO",
        },
        created_at=now,
    )


HEALTHY_ANALYSIS = create_analysis(
    "analysis-demo-22",
    22,
    "STABLE",
    "NO_ALERT",
)

DECLINING_ANALYSIS = create_analysis(
    "analysis-demo-55",
    55,
    "WATCH",
    "NO_ALERT",
)

CORAL_ANALYSIS = create_analysis(
    "analysis-demo-88",
    88,
    "CRITICAL",
    "ALERT_DISPATCHED",
)