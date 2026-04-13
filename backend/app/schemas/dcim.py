"""Pydantic-skjemaer for DCIM API."""

from __future__ import annotations

import datetime as dt
import re
from typing import Any

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
    height_mm: int | None = Field(None, ge=1, le=100_000)
    width_mm: int | None = Field(None, ge=1, le=100_000)
    depth_mm: int | None = Field(None, ge=1, le=100_000)
    brand: str | None = Field(None, max_length=255)
    purchase_date: dt.date | None = None
    commissioned_date: dt.date | None = None
    notes: str | None = None
    attributes: dict[str, Any] | None = None


class RackUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    u_height: int | None = Field(None, ge=1, le=64)
    sort_order: int | None = None
    height_mm: int | None = Field(None, ge=1, le=100_000)
    width_mm: int | None = Field(None, ge=1, le=100_000)
    depth_mm: int | None = Field(None, ge=1, le=100_000)
    brand: str | None = Field(None, max_length=255)
    purchase_date: dt.date | None = None
    commissioned_date: dt.date | None = None
    notes: str | None = None
    attributes: dict[str, Any] | None = None


class RackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    name: str
    u_height: int
    sort_order: int
    height_mm: int | None
    width_mm: int | None
    depth_mm: int | None
    brand: str | None
    purchase_date: dt.date | None
    commissioned_date: dt.date | None
    notes: str | None
    attributes: dict[str, Any] | None


class ManufacturerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    website_url: str | None = Field(None, max_length=1024)


class ManufacturerUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    website_url: str | None = Field(None, max_length=1024)
    iana_enterprise_number: int | None = Field(None, ge=0, le=2147483647)


class ManufacturerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    website_url: str | None
    has_logo: bool
    iana_enterprise_number: int | None = None


class DeviceTypeCreate(BaseModel):
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


class DeviceTypeUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class DeviceTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None


class DeviceModelBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    u_height: int
    device_type_id: int | None
    snmp_sys_object_id_prefix: str | None = None


class ManufacturerDetailRead(BaseModel):
    id: int
    name: str
    description: str | None
    website_url: str | None
    has_logo: bool
    iana_enterprise_number: int | None = None
    device_models: list[DeviceModelBrief]


class DeviceModelCreate(BaseModel):
    manufacturer_id: int | None = None
    device_type_id: int | None = None
    name: str = Field(..., min_length=1, max_length=255)
    u_height: int = Field(1, ge=0, le=64)
    form_factor: str | None = Field(None, max_length=64)
    image_front_url: str | None = Field(None, max_length=1024)
    image_back_url: str | None = Field(None, max_length=1024)
    image_product_url: str | None = Field(None, max_length=1024)
    snmp_sys_object_id_prefix: str | None = Field(None, max_length=512)


class DeviceModelUpdate(BaseModel):
    manufacturer_id: int | None = None
    device_type_id: int | None = None
    name: str | None = Field(None, min_length=1, max_length=255)
    u_height: int | None = Field(None, ge=0, le=64)
    form_factor: str | None = Field(None, max_length=64)
    image_front_url: str | None = Field(None, max_length=1024)
    image_back_url: str | None = Field(None, max_length=1024)
    image_product_url: str | None = Field(None, max_length=1024)
    snmp_sys_object_id_prefix: str | None = Field(None, max_length=512)


class DeviceModelRead(BaseModel):
    """Bygges eksplisitt i tjenesten (inkl. has_image_* fra relpath)."""

    id: int
    manufacturer_id: int | None
    device_type_id: int | None
    name: str
    u_height: int
    form_factor: str | None
    image_front_url: str | None
    image_back_url: str | None
    image_product_url: str | None
    has_image_front_file: bool
    has_image_back_file: bool
    has_image_product_file: bool
    snmp_sys_object_id_prefix: str | None = None


class DeviceInstanceCreate(BaseModel):
    device_model_id: int | None = None
    device_type_id: int | None = None
    name: str = Field(..., min_length=1, max_length=255)
    serial_number: str | None = Field(None, max_length=128)
    asset_tag: str | None = Field(None, max_length=128)
    attributes: dict[str, Any] | None = None


class DeviceInstanceUpdate(BaseModel):
    device_model_id: int | None = None
    device_type_id: int | None = None
    name: str | None = Field(None, min_length=1, max_length=255)
    serial_number: str | None = Field(None, max_length=128)
    asset_tag: str | None = Field(None, max_length=128)
    attributes: dict[str, Any] | None = None


class DeviceInstanceRead(BaseModel):
    """Bygges i tjenesten (effective_device_type_id fra modell eller override)."""

    id: int
    device_model_id: int | None
    device_type_id: int | None
    effective_device_type_id: int | None
    # Site fra rack → rom når enheten er plassert; brukes bl.a. for IPAM-prefiks i riktig site.
    effective_site_id: int | None
    name: str
    serial_number: str | None
    asset_tag: str | None
    attributes: dict[str, Any] = Field(default_factory=dict)


class DeviceInterfaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    mac_address: str | None = Field(None, max_length=32)
    speed_mbps: int | None = Field(None, ge=0, le=1_000_000_000)
    mtu: int | None = Field(None, ge=68, le=65535)
    vlan_id: int | None = Field(None, ge=1, le=4094)
    enabled: bool = True
    sort_order: int = 0
    parent_interface_id: int | None = Field(None, ge=1)


class DeviceInterfaceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None
    mac_address: str | None = Field(None, max_length=32)
    speed_mbps: int | None = Field(None, ge=0, le=1_000_000_000)
    mtu: int | None = Field(None, ge=68, le=65535)
    vlan_id: int | None = Field(None, ge=1, le=4094)
    enabled: bool | None = None
    sort_order: int | None = None
    parent_interface_id: int | None = Field(None, ge=1)


class IpAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    interface_id: int
    ipv4_prefix_id: int | None = None
    family: str
    address: str
    is_primary: bool


class DeviceInterfaceRead(BaseModel):
    """Bygges i tjenesten (ip_assignments inkludert)."""

    id: int
    device_id: int
    parent_interface_id: int | None
    name: str
    description: str | None
    mac_address: str | None
    speed_mbps: int | None
    mtu: int | None
    vlan_id: int | None
    enabled: bool
    sort_order: int
    ip_assignments: list[IpAssignmentRead] = Field(default_factory=list)


class IpAssignmentCreate(BaseModel):
    address: str = Field(..., min_length=1, max_length=45)
    is_primary: bool = False
    ipv4_prefix_id: int | None = None


class IpAssignmentUpdate(BaseModel):
    is_primary: bool | None = None
    ipv4_prefix_id: int | None = None


class DeviceIpAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    ipv4_prefix_id: int | None = None
    family: str
    address: str
    is_primary: bool


class DeviceIpAssignmentCreate(BaseModel):
    address: str = Field(..., min_length=1, max_length=45)
    is_primary: bool = False
    ipv4_prefix_id: int | None = None


class DeviceIpAssignmentUpdate(BaseModel):
    is_primary: bool | None = None
    ipv4_prefix_id: int | None = None


class RackPlacementCreate(BaseModel):
    rack_id: int
    device_id: int
    u_position: int = Field(..., ge=0)
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


class RackPlacementUpdate(BaseModel):
    rack_id: int | None = None
    u_position: int | None = Field(None, ge=0)
    mounting: str | None = Field(None, max_length=16)

    @field_validator("mounting")
    @classmethod
    def mounting_ok(cls, v: str | None) -> str | None:
        if v is None:
            return None
        x = v.lower().strip()
        if x not in ("front", "rear"):
            raise ValueError("mounting må være front eller rear")
        return x
