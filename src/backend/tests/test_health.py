from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_standard_response() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "message": "success",
        "data": {"status": "ok"},
    }
