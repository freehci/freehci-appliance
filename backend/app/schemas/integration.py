"""Skjemaer for tilkoblinger og identitetskonflikter."""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.secret_ref import normalize_secret_ref

CONNECTION_STATUSES = frozenset({"planned", "ready", "disabled", "error"})
IDENTITY_TYPES = frozenset({"serial", "uuid", "asset_tag", "redfish", "other"})


class IntegrationConnectionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    plugin_id: str = Field(..., min_length=1, max_length=128)
    base_url: str | None = Field(None, max_length=1024)
    credential_ref: str | None = None
    status: str = "planned"
    mapping_json: dict | None = None
    description: str | None = None

    @field_validator("status")
    @classmethod
    def status_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in CONNECTION_STATUSES:
            raise ValueError(f"status må være en av: {', '.join(sorted(CONNECTION_STATUSES))}")
        return s

    @field_validator("credential_ref")
    @classmethod
    def cred_ok(cls, v: str | None) -> str | None:
        return normalize_secret_ref(v)


class IntegrationConnectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    plugin_id: str
    base_url: str | None
    credential_ref: str | None
    status: str
    last_sync_at: dt.datetime | None
    mapping_json: dict | None
    description: str | None
    created_at: dt.datetime


class DeviceIdentityIngest(BaseModel):
    identity_type: str
    namespace: str = "default"
    value: str = Field(..., min_length=1, max_length=255)
    device_id: int | None = Field(None, ge=1)
    name: str | None = Field(None, max_length=255)
    create_if_missing: bool = False

    @field_validator("identity_type")
    @classmethod
    def type_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in IDENTITY_TYPES:
            raise ValueError(f"identity_type må være en av: {', '.join(sorted(IDENTITY_TYPES))}")
        return s

    @field_validator("namespace")
    @classmethod
    def ns_ok(cls, v: str) -> str:
        s = v.strip().lower()
        return s or "default"


class DeviceIdentityIngestRead(BaseModel):
    action: str
    device_id: int | None
    identity_id: int | None
    conflict_id: int | None
    created: bool = False


class IdentityConflictRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    identity_type: str
    namespace: str
    value: str
    connection_a_id: int | None
    connection_b_id: int | None
    device_a_id: int | None
    device_b_id: int | None
    status: str
    created_at: dt.datetime


EXTERNAL_OBJECT_TYPES = frozenset({"device"})
OWNED_DEVICE_FIELDS = frozenset(
    {
        "name",
        "serial_number",
        "asset_tag",
        "site_id",
        "device_role_id",
        "device_type_id",
        "device_model_id",
    }
)


class ExternalObjectMappingCreate(BaseModel):
    """Eksplisitt ekstern ID. infer_*/navn-matching avvises (extra=forbid)."""

    model_config = ConfigDict(extra="forbid")

    connection_id: int = Field(..., ge=1)
    object_type: str = "device"
    external_id: str = Field(..., min_length=1, max_length=255)
    device_id: int | None = Field(None, ge=1)

    @field_validator("object_type")
    @classmethod
    def type_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in EXTERNAL_OBJECT_TYPES:
            raise ValueError(f"object_type må være en av: {', '.join(sorted(EXTERNAL_OBJECT_TYPES))}")
        return s

    @field_validator("external_id")
    @classmethod
    def ext_ok(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("external_id kan ikke være tom")
        return s


class ExternalObjectMappingUpdate(BaseModel):
    """Kun typet device_id. None fjerner binding; navn brukes aldri."""

    model_config = ConfigDict(extra="forbid")

    device_id: int | None = Field(None, ge=1)


class ExternalObjectMappingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    connection_id: int
    object_type: str
    external_id: str
    device_id: int | None
    created_at: dt.datetime


class FieldOwnershipCreate(BaseModel):
    """Ett felt, én tilkobling. mapping_json og infer_* avvises."""

    model_config = ConfigDict(extra="forbid")

    connection_id: int = Field(..., ge=1)
    device_id: int = Field(..., ge=1)
    field_name: str = Field(..., min_length=1, max_length=64)

    @field_validator("field_name")
    @classmethod
    def field_ok(cls, v: str) -> str:
        s = v.strip()
        if s not in OWNED_DEVICE_FIELDS:
            raise ValueError(f"field_name må være en av: {', '.join(sorted(OWNED_DEVICE_FIELDS))}")
        return s


class FieldOwnershipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    connection_id: int
    device_id: int
    field_name: str
    created_at: dt.datetime
