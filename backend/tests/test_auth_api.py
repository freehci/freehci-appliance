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
