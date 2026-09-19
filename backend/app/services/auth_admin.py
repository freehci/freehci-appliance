"""Admin-innlogging, passord, kontoer og API-nøkler."""

from __future__ import annotations

import datetime as dt
import hashlib
import secrets
from typing import Any

import jwt
from fastapi import HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth_password import hash_password, verify_password
from app.core.config import Settings, get_settings
from app.models.admin_account import AdminAccount
from app.models.api_token import ApiToken
from app.models.iam import User
from app.schemas.auth import AdminAccountRead, ApiTokenCreated, ApiTokenRead

API_TOKEN_PREFIX = "fhci_"


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


def _account_read(row: AdminAccount, current_id: int) -> AdminAccountRead:
    return AdminAccountRead(
        id=row.id,
        username=row.username,
        updated_at=row.updated_at,
        is_self=row.id == current_id,
    )


def list_admin_accounts(db: Session, current: AdminAccount) -> list[AdminAccountRead]:
    rows = db.execute(select(AdminAccount).order_by(AdminAccount.username)).scalars().all()
    return [_account_read(r, current.id) for r in rows]


def create_admin_account(db: Session, current: AdminAccount, username: str, password: str) -> AdminAccountRead:
    row = AdminAccount(username=username.strip(), password_hash=hash_password(password))
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="brukernavn er opptatt") from None
    db.refresh(row)
    return _account_read(row, current.id)


def reset_admin_password(db: Session, account_id: int, new_password: str) -> None:
    row = db.get(AdminAccount, account_id)
    if row is None:
        raise HTTPException(status_code=404, detail="bruker ikke funnet")
    row.password_hash = hash_password(new_password)
    db.commit()


def delete_admin_account(db: Session, current: AdminAccount, account_id: int) -> None:
    row = db.get(AdminAccount, account_id)
    if row is None:
        raise HTTPException(status_code=404, detail="bruker ikke funnet")
    if row.id == current.id:
        raise HTTPException(status_code=400, detail="kan ikke slette innlogget bruker")
    n = db.execute(select(func.count()).select_from(AdminAccount)).scalar_one()
    if int(n) <= 1:
        raise HTTPException(status_code=400, detail="kan ikke slette siste innloggingsbruker")
    db.execute(delete(ApiToken).where(ApiToken.admin_id == row.id))
    db.delete(row)
    db.commit()


def _hash_api_token(plain: str) -> str:
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


def _aware(value: dt.datetime | None) -> dt.datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=dt.UTC)
    return value


def _token_read(row: ApiToken) -> ApiTokenRead:
    return ApiTokenRead(
        id=row.id,
        name=row.name,
        token_prefix=row.token_prefix,
        created_at=row.created_at,
        last_used_at=row.last_used_at,
        expires_at=row.expires_at,
        user_id=row.user_id,
        scopes=list(row.scopes) if getattr(row, "scopes", None) else None,
    )


def list_api_tokens(db: Session, user_id: int | None = None) -> list[ApiTokenRead]:
    q = select(ApiToken)
    if user_id is not None:
        q = q.where(ApiToken.user_id == user_id)
    rows = db.execute(q.order_by(ApiToken.created_at.desc())).scalars().all()
    return [_token_read(r) for r in rows]


def create_api_token(
    db: Session,
    admin: AdminAccount,
    name: str,
    *,
    user: User | None = None,
    scopes: list[str] | None = None,
) -> ApiTokenCreated:
    if user is not None and (user.kind or "person") != "service_account":
        raise HTTPException(status_code=400, detail="API-nøkler kan bare knyttes til servicekontoer")
    raw = secrets.token_urlsafe(32)
    token = f"{API_TOKEN_PREFIX}{raw}"
    row = ApiToken(
        name=name.strip(),
        token_prefix=token[:12],
        token_hash=_hash_api_token(token),
        admin_id=admin.id,
        user_id=user.id if user is not None else None,
        scopes=scopes,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return ApiTokenCreated(**_token_read(row).model_dump(), token=token)


def delete_api_token(db: Session, token_id: int, *, user_id: int | None = None) -> None:
    row = db.get(ApiToken, token_id)
    if row is None or (user_id is not None and row.user_id != user_id):
        raise HTTPException(status_code=404, detail="api-nøkkel ikke funnet")
    db.delete(row)
    db.commit()


def authenticate_api_token(db: Session, token: str) -> ApiToken | None:
    """Returner gyldig API-nøkkel, ellers None."""
    if not token.startswith(API_TOKEN_PREFIX):
        return None
    digest = _hash_api_token(token)
    row = db.execute(select(ApiToken).where(ApiToken.token_hash == digest)).scalar_one_or_none()
    if row is None:
        return None
    now = dt.datetime.now(dt.UTC)
    exp = _aware(row.expires_at)
    if exp is not None and exp <= now:
        return None
    last = _aware(row.last_used_at)
    if last is None or (now - last).total_seconds() >= 60:
        row.last_used_at = now
        db.commit()
    return row
