"""Skjemaer for tenants."""

from __future__ import annotations

import datetime as dt
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class TenantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=64)
    description: str | None = None

    @field_validator("slug")
    @classmethod
    def slug_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if not _SLUG_RE.match(s):
            raise ValueError("slug må være lowercase bokstaver, tall og bindestrek")
        return s


class TenantUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class TenantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None
    created_at: dt.datetime


TenantDcimScopeType = Literal["site", "room", "rack"]
TenantDcimAccess = Literal["view", "manage"]


class TenantUserMembershipCreate(BaseModel):
    user_id: int = Field(..., ge=1)
    role: str = Field("member", min_length=1, max_length=64)


class TenantUserMembershipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    user_id: int
    role: str
    created_at: dt.datetime


class TenantDcimGrantCreate(BaseModel):
    scope_type: TenantDcimScopeType
    scope_id: int = Field(..., ge=1)
    access: TenantDcimAccess = "view"


class TenantDcimGrantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    scope_type: str
    scope_id: int
    access: str
    created_at: dt.datetime


class UserAccessibleSitesRead(BaseModel):
    """Effektive DCIM-site-id-er for en IAM-bruker (policy-aggregering)."""

    user_id: int
    site_ids: list[int]
