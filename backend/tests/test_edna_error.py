from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_invalid_edna_sample_returns_structured_error():
    response = client.get("/api/edna/matches/not-a-valid-sample")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Sample not found"
    }


def test_invalid_edna_sample_does_not_crash_backend():
    response = client.get("/api/edna/matches/not-a-valid-sample")

    assert response.status_code != 500
    assert "detail" in response.json()