from fastapi.testclient import TestClient

from app.main import create_app


def test_live() -> None:
    app = create_app()
    with TestClient(app) as client:
        r = client.get("/api/v1/health/live")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
