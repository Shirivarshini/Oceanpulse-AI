from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


EXPECTED = {
    "healthy_reef": (22, "STABLE", "NO_ALERT"),
    "declining_fishery": (55, "WATCH", "NO_ALERT"),
    "coral_bleaching": (88, "CRITICAL", "ALERT_DISPATCHED"),
}


def test_backend_demo_scenarios_preserve_fallback_sources():
    for scenario, (index, level, alert) in EXPECTED.items():
        response = client.post(
            "/api/demo/analyze",
            json={"scenario": scenario},
        )

        assert response.status_code == 200

        body = response.json()

        assert body["index"] == index
        assert body["level"] == level
        assert body["alert"]["status"] == alert

        assert body["sources"] == {
            "ocean": "DEMO",
            "fisheries": "DEMO",
            "molecular": "DEMO",
        }


def test_backend_never_reports_unavailable_sources_as_live():
    response = client.post(
        "/api/demo/analyze",
        json={"scenario": "coral_bleaching"},
    )

    assert response.status_code == 200

    sources = response.json()["sources"]

    assert all(status != "LIVE" for status in sources.values())