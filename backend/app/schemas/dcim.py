"""Pydantic-skjemaer for DCIM API."""

from __future__ import annotations

import datetime as dt
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class SiteCreate(BaseModel):
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


class SiteUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class SiteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None
    created_at: dt.datetime


class RoomCreate(BaseModel):
    site_id: int
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class RoomUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class RoomRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    site_id: int
    name: str
    description: str | None


class RackCreate(BaseModel):
    room_id: int
    name: str = Field(..., min_length=1, max_length=255)
    u_height: int = Field(42, ge=1, le=64)
    sort_order: int = 0


class RackUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    u_height: int | None = Field(None, ge=1, le=64)
    sort_order: int | None = None


class RackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    name: str
    u_height: int
    sort_order: int


class ManufacturerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class ManufacturerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class DeviceModelCreate(BaseModel):
    manufacturer_id: int | None = None
    name: str = Field(..., min_length=1, max_length=255)
    u_height: int = Field(1, ge=1, le=64)
    form_factor: str | None = Field(None, max_length=64)


class DeviceModelUpdate(BaseModel):
    manufacturer_id: int | None = None
    name: str | None = Field(None, min_length=1, max_length=255)
    u_height: int | None = Field(None, ge=1, le=64)
    form_factor: str | None = Field(None, max_length=64)


class DeviceModelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    manufacturer_id: int | None
    name: str
    u_height: int
    form_factor: str | None


class DeviceInstanceCreate(BaseModel):
    device_model_id: int | None = None
    name: str = Field(..., min_length=1, max_length=255)
    serial_number: str | None = Field(None, max_length=128)
    asset_tag: str | None = Field(None, max_length=128)


class DeviceInstanceUpdate(BaseModel):
    device_model_id: int | None = None
    name: str | None = Field(None, min_length=1, max_length=255)
    serial_number: str | None = Field(None, max_length=128)
    asset_tag: str | None = Field(None, max_length=128)


class DeviceInstanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_model_id: int | None
    name: str
    serial_number: str | None
    asset_tag: str | None


class RackPlacementCreate(BaseModel):
    rack_id: int
    device_id: int
    u_position: int = Field(..., ge=1)
    mounting: str = Field(default="front", max_length=16)

    @field_validator("mounting")
    @classmethod
    def mounting_ok(cls, v: str) -> str:
        x = v.lower().strip()
        if x not in ("front", "rear"):
            raise ValueError("mounting må være front eller rear")
        return x


class RackPlacementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rack_id: int
    device_id: int
    u_position: int
    mounting: str
