from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal


AlertStatus = Literal[
    "NO_ALERT",
    "ALERT_DISPATCHED",
    "ALERT_BLOCKED_STALE",
]


DEFAULT_THRESHOLD = 70


@dataclass
class AlertDecision:
    status: AlertStatus
    threshold: int
    reason: str


def evaluate_alert(
    index: int,
    created_at: datetime,
    threshold: int = DEFAULT_THRESHOLD,
    max_age_seconds: int = 3600,
) -> AlertDecision:
    now = datetime.now(timezone.utc)

    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    age_seconds = (now - created_at).total_seconds()

    if age_seconds > max_age_seconds:
        return AlertDecision(
            status="ALERT_BLOCKED_STALE",
            threshold=threshold,
            reason="Alert blocked because analysis data is stale.",
        )

    if index >= threshold:
        return AlertDecision(
            status="ALERT_DISPATCHED",
            threshold=threshold,
            reason="Ecosystem index reached or exceeded the alert threshold.",
        )

    return AlertDecision(
        status="NO_ALERT",
        threshold=threshold,
        reason="Ecosystem index is below the alert threshold.",
    )