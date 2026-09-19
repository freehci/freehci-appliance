"""Auth (lokal admin og API-nøkler)."""

import datetime as dt

from pydantic import BaseModel, Field


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


class ApiTokenCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)


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
