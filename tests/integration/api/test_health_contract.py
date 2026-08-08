from fastapi.testclient import TestClient

from app.main import app


def test_health_contract() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"code", "message", "data"}
    assert payload["code"] == 0
