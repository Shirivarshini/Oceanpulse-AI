from datetime import datetime, timedelta, timezone

from backend.app.alert_gate import evaluate_alert


def test_backend_alert_gate_blocks_stale_analysis():
    created_at = datetime.now(timezone.utc) - timedelta(hours=2)

    decision = evaluate_alert(
        index=88,
        created_at=created_at,
        threshold=70,
    )

    assert decision.status == "ALERT_BLOCKED_STALE"
    assert decision.threshold == 70