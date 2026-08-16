from datetime import datetime, timedelta, timezone

from app.alert_gate import evaluate_alert


def test_below_threshold_returns_no_alert():
    created_at = datetime.now(timezone.utc)

    result = evaluate_alert(
        index=45,
        created_at=created_at,
    )

    assert result.status == "NO_ALERT"
    assert result.threshold == 70


def test_at_or_above_threshold_dispatches_alert():
    created_at = datetime.now(timezone.utc)

    result = evaluate_alert(
        index=87,
        created_at=created_at,
    )

    assert result.status == "ALERT_DISPATCHED"
    assert result.threshold == 70


def test_stale_analysis_blocks_alert():
    created_at = datetime.now(timezone.utc) - timedelta(hours=2)

    result = evaluate_alert(
        index=87,
        created_at=created_at,
    )

    assert result.status == "ALERT_BLOCKED_STALE"
    assert result.threshold == 70