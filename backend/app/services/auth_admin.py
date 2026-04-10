"""Admin-innlogging og passord."""

from __future__ import annotations

import datetime as dt
from typing import Any

import jwt
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.auth_password import hash_password, verify_password
from app.core.config import Settings, get_settings
from app.models.admin_account import AdminAccount


def ensure_default_admin(db: Session) -> None:
    """Opprett admin/admin hvis ingen admin-konto finnes."""
    n = db.execute(select(func.count()).select_from(AdminAccount)).scalar_one()
    if int(n) > 0:
        return
    db.add(
        AdminAccount(
            username="admin",
            password_hash=hash_password("admin"),
        )
    )
    db.commit()


def _jwt_settings(settings: Settings) -> tuple[str, int]:
    secret = settings.jwt_secret.get_secret_value()
    return secret, settings.jwt_expire_minutes


def create_access_token(admin_id: int, username: str, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    secret, minutes = _jwt_settings(settings)
    now = dt.datetime.now(dt.UTC)
    exp = now + dt.timedelta(minutes=minutes)
    payload: dict[str, Any] = {
        "sub": str(admin_id),
        "usr": username,
        "iat": int(now.timestamp()),
        "exp": exp,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token_payload(token: str, settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    secret, _ = _jwt_settings(settings)
    return jwt.decode(token, secret, algorithms=["HS256"])


def authenticate_admin(db: Session, username: str, password: str) -> AdminAccount | None:
    row = db.execute(select(AdminAccount).where(AdminAccount.username == username)).scalar_one_or_none()
    if row is None:
        return None
    if not verify_password(password, row.password_hash):
        return None
    return row


def login_admin(db: Session, username: str, password: str) -> str:
    row = authenticate_admin(db, username.strip(), password)
    if row is None:
        raise HTTPException(status_code=401, detail="feil brukernavn eller passord")
    return create_access_token(row.id, row.username)


def change_admin_password(db: Session, admin: AdminAccount, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, admin.password_hash):
        raise HTTPException(status_code=400, detail="nåværende passord er feil")
    admin.password_hash = hash_password(new_password)
    db.commit()
