"""API-auth med JWT (FREEHCI_SKIP_AUTH av i denne modulen)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.auth_password import hash_password
from app.core.config import get_settings
from app.core.db import SessionLocal
from app.main import create_app
from app.models.admin_account import AdminAccount


def _reset_admin_password_to_default() -> None:
    db = SessionLocal()
    try:
        row = db.execute(select(AdminAccount).where(AdminAccount.username == "admin")).scalar_one_or_none()
        if row is not None:
            row.password_hash = hash_password("admin")
            db.commit()
    finally:
        db.close()


@pytest.fixture
def client_with_auth(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("FREEHCI_SKIP_AUTH", "0")
    get_settings.cache_clear()
    app = create_app()
    with TestClient(app) as c:
        yield c
    _reset_admin_password_to_default()
    monkeypatch.setenv("FREEHCI_SKIP_AUTH", "1")
    get_settings.cache_clear()


def test_dcim_unauthorized_without_token(client_with_auth: TestClient) -> None:
    r = client_with_auth.get("/api/v1/dcim/sites")
    assert r.status_code == 401


def test_dcim_logo_and_model_images_get_without_bearer(client_with_auth: TestClient) -> None:
    """<img src> sender ikke JWT — skal nå ruten (404 uten fil), ikke 401."""
    assert client_with_auth.get("/api/v1/dcim/manufacturers/999999/logo").status_code == 404
    assert client_with_auth.get("/api/v1/dcim/device-models/999999/image-front").status_code == 404
    assert client_with_auth.get("/api/v1/dcim/device-models/999999/image-back").status_code == 404
    assert client_with_auth.get("/api/v1/dcim/device-models/999999/image-product").status_code == 404


def test_dcim_logo_upload_still_requires_bearer(client_with_auth: TestClient) -> None:
    r = client_with_auth.post(
        "/api/v1/dcim/manufacturers/1/logo",
        files={"file": ("x.png", b"x", "image/png")},
    )
    assert r.status_code == 401


def test_login_and_bearer_access(client_with_auth: TestClient) -> None:
    r = client_with_auth.post("/api/v1/auth/login", json={"username": "admin", "password": "admin"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    sites = client_with_auth.get(
        "/api/v1/dcim/sites",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert sites.status_code == 200


def test_change_password(client_with_auth: TestClient) -> None:
    login = client_with_auth.post("/api/v1/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    ch = client_with_auth.post(
        "/api/v1/auth/change-password",
        json={"current_password": "admin", "new_password": "nyttpass8"},
        headers=headers,
    )
    assert ch.status_code == 204
    bad = client_with_auth.post("/api/v1/auth/login", json={"username": "admin", "password": "admin"})
    assert bad.status_code == 401
    ok = client_with_auth.post("/api/v1/auth/login", json={"username": "admin", "password": "nyttpass8"})
    assert ok.status_code == 200


def test_admin_accounts_reset_and_delete(client_with_auth: TestClient) -> None:
    login = client_with_auth.post("/api/v1/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    created = client_with_auth.post(
        "/api/v1/auth/accounts",
        json={"username": "operatør", "password": "hemmelig1"},
        headers=headers,
    )
    assert created.status_code == 200, created.text
    other_id = created.json()["id"]
    assert created.json()["is_self"] is False

    listed = client_with_auth.get("/api/v1/auth/accounts", headers=headers)
    assert listed.status_code == 200
    names = {x["username"] for x in listed.json()}
    assert {"admin", "operatør"} <= names

    me = client_with_auth.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    self_id = me.json()["id"]
    assert client_with_auth.delete(f"/api/v1/auth/accounts/{self_id}", headers=headers).status_code == 400

    reset = client_with_auth.post(
        f"/api/v1/auth/accounts/{other_id}/reset-password",
        json={"new_password": "nyttpass9"},
        headers=headers,
    )
    assert reset.status_code == 204
    assert client_with_auth.post("/api/v1/auth/login", json={"username": "operatør", "password": "hemmelig1"}).status_code == 401
    assert client_with_auth.post("/api/v1/auth/login", json={"username": "operatør", "password": "nyttpass9"}).status_code == 200

    deleted = client_with_auth.delete(f"/api/v1/auth/accounts/{other_id}", headers=headers)
    assert deleted.status_code == 204
    leftover = client_with_auth.get("/api/v1/auth/accounts", headers=headers)
    assert {x["username"] for x in leftover.json()} == {"admin"}


def test_api_token_bearer_and_agent_discovery(client_with_auth: TestClient) -> None:
    login = client_with_auth.post("/api/v1/auth/login", json={"username": "admin", "password": "admin"})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    created = client_with_auth.post("/api/v1/auth/tokens", json={"name": "agent-cursor"}, headers=headers)
    assert created.status_code == 200, created.text
    token = created.json()["token"]
    assert token.startswith("fhci_")
    token_id = created.json()["id"]

    sites = client_with_auth.get("/api/v1/dcim/sites", headers={"Authorization": f"Bearer {token}"})
    assert sites.status_code == 200

    agent = client_with_auth.get("/api/v1/auth/agent")
    assert agent.status_code == 200
    body = agent.json()
    assert body["openapi_url"] == "/api/v1/openapi.json"
    assert body["docs_url"] == "/api/v1/docs"

    spec = client_with_auth.get("/api/v1/openapi.json")
    assert spec.status_code == 200
    assert spec.json()["components"]["securitySchemes"]["BearerAuth"]["scheme"] == "bearer"

    assert client_with_auth.delete(f"/api/v1/auth/tokens/{token_id}", headers=headers).status_code == 204
    denied = client_with_auth.get("/api/v1/dcim/sites", headers={"Authorization": f"Bearer {token}"})
    assert denied.status_code == 401
