"""Skjemaer for IAM-katalog (personer via `users`, roller, grupper)."""

from __future__ import annotations

import datetime as dt
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.ipam import UserCreate, UserRead

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,62}$")


class IamNamedCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=64)
    description: str | None = None

    @field_validator("slug", mode="before")
    @classmethod
    def slug_fmt(cls, v: str) -> str:
        s = str(v).strip().lower()
        if not _SLUG_RE.match(s):
            raise ValueError("slug må være små bokstaver, tall, _ eller - (1–63 tegn)")
        return s


class IamRoleCreate(IamNamedCreate):
    """Opprett global IAM-rolle."""


class IamGroupCreate(IamNamedCreate):
    external_subject_id: str | None = Field(None, max_length=512)
    identity_provider: str | None = Field(None, max_length=128)


class IamRoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None
    system: bool
    created_at: dt.datetime


class IamRoleUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class IamGroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None
    external_subject_id: str | None
    identity_provider: str | None
    created_at: dt.datetime


class IamGroupUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class IamRef(BaseModel):
    id: int
    name: str
    slug: str


class PersonDetailRead(UserRead):
    roles: list[IamRef]
    groups_direct: list[IamRef]
    groups_effective: list[IamRef]


class IamPersonBrief(BaseModel):
    id: int
    username: str
    display_name: str | None


class IamRoleDetailRead(IamRoleRead):
    member_count: int
    assignees: list[IamPersonBrief]


class IamGroupMemberUserRead(BaseModel):
    user_id: int
    username: str
    display_name: str | None


class IamGroupMemberSubgroupRead(BaseModel):
    child_group_id: int
    name: str
    slug: str


class IamGroupDetailRead(IamGroupRead):
    direct_users: list[IamGroupMemberUserRead]
    direct_subgroups: list[IamGroupMemberSubgroupRead]
    effective_user_ids: list[int]


class IamGroupAddUserMember(BaseModel):
    user_id: int = Field(..., ge=1)


class IamGroupAddSubgroupMember(BaseModel):
    child_group_id: int = Field(..., ge=1)


class IamAssignRoleBody(BaseModel):
    role_id: int = Field(..., ge=1)


# Re-export for router convenience
PersonCreate = UserCreate
