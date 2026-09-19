"""Auth (lokal admin og API-nøkler)."""

import datetime as dt

from pydantic import BaseModel, Field, field_validator

from app.core.request_context import IPAM_SCOPES


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminMeResponse(BaseModel):
    id: int
    username: str


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=256)
    new_password: str = Field(..., min_length=8, max_length=256)


class AdminAccountRead(BaseModel):
    id: int
    username: str
    updated_at: dt.datetime
    is_self: bool = False


class AdminAccountCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=8, max_length=256)


class AdminResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=256)


class ApiTokenRead(BaseModel):
    id: int
    name: str
    token_prefix: str
    created_at: dt.datetime
    last_used_at: dt.datetime | None
    expires_at: dt.datetime | None
    user_id: int | None = None
    scopes: list[str] | None = None


class ApiTokenCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    scopes: list[str] | None = None

    @field_validator("scopes")
    @classmethod
    def scopes_ok(cls, v: list[str] | None) -> list[str] | None:
        if not v:
            return None
        cleaned = [s.strip() for s in v if s and s.strip()]
        unknown = [s for s in cleaned if s not in IPAM_SCOPES]
        if unknown:
            raise ValueError(f"ukjent scope: {', '.join(unknown)}")
        return cleaned or None


class ApiTokenCreated(ApiTokenRead):
    token: str


class AgentAuthHint(BaseModel):
    type: str
    header: str
    login_url: str
    tokens_url: str
    token_prefix: str
    notes: list[str]


class AgentConnectInfo(BaseModel):
    app_name: str
    api_prefix: str
    openapi_url: str
    docs_url: str
    auth: AgentAuthHint
