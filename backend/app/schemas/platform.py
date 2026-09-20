"""Skjemaer for cluster-inventar."""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field, field_validator

CLUSTER_KINDS = frozenset({"proxmox", "talos", "other"})
MEMBER_ROLES = frozenset({"node", "control", "worker", "other"})


class PlatformClusterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    kind: str = "other"
    site_id: int | None = Field(None, ge=1)
    description: str | None = None

    @field_validator("kind")
    @classmethod
    def kind_ok(cls, v: str) -> str:
        s = (v or "").strip().lower() or "other"
        if s not in CLUSTER_KINDS:
            raise ValueError(f"kind må være en av: {', '.join(sorted(CLUSTER_KINDS))}")
        return s


class PlatformClusterMemberCreate(BaseModel):
    device_id: int = Field(..., ge=1)
    role: str = "node"

    @field_validator("role")
    @classmethod
    def role_ok(cls, v: str) -> str:
        s = (v or "").strip().lower() or "node"
        if s not in MEMBER_ROLES:
            raise ValueError(f"role må være en av: {', '.join(sorted(MEMBER_ROLES))}")
        return s


class PlatformClusterMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cluster_id: int
    device_id: int
    role: str
    created_at: dt.datetime


class PlatformClusterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    kind: str
    site_id: int | None
    description: str | None
    created_at: dt.datetime
    members: list[PlatformClusterMemberRead] = Field(default_factory=list)
