"""Skjemaer for IPAM API (IPv4 prefiks per site)."""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Ipv4PrefixCreate(BaseModel):
    site_id: int
    name: str = Field(..., min_length=1, max_length=255)
    cidr: str = Field(..., min_length=1, max_length=32)
    description: str | None = None

    @field_validator("cidr")
    @classmethod
    def cidr_not_empty(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("cidr kan ikke være tom")
        return s


class Ipv4PrefixUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    cidr: str | None = Field(None, min_length=1, max_length=32)
    description: str | None = None

    @field_validator("cidr")
    @classmethod
    def cidr_strip(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if not s:
            raise ValueError("cidr kan ikke være tom")
        return s


class Ipv4PrefixRead(BaseModel):
    """Returneres fra tjenestelaget med telling fra DCIM IP-tildelinger."""

    id: int
    site_id: int
    name: str
    cidr: str
    description: str | None
    created_at: dt.datetime
    used_count: int = Field(
        description=(
            "Antall IPv4-tildelinger der adressen ligger i dette CIDR-et og enheten er "
            "plassert på samme site (uavhengig av om tildelingen peker på et mer spesifikt prefiks, f.eks. /32)"
        ),
    )
    address_total: int = Field(description="Totalt antall IPv4-adresser i CIDR (inkl. nettverk/broadcast der relevant)")


class Ipv4AssignmentInPrefixRead(BaseModel):
    assignment_id: int
    address: str
    ipv4_prefix_id: int | None
    interface_id: int
    interface_name: str
    device_id: int
    device_name: str


class Ipv4PrefixExploreRead(BaseModel):
    """Undprefiks og alle IPv4-tildelinger innenfor et prefiks (samme site)."""

    prefix: Ipv4PrefixRead
    child_prefixes: list[Ipv4PrefixRead]
    assignments: list[Ipv4AssignmentInPrefixRead]


class SubnetScanCreate(BaseModel):
    ipv4_prefix_id: int = Field(..., ge=1)


class SubnetScanHostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    address: str
    mac_address: str | None
    ping_responded: bool


class SubnetScanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    site_id: int
    ipv4_prefix_id: int | None
    cidr: str
    method: str
    status: str
    hosts_scanned: int
    hosts_responding: int
    error_message: str | None
    started_at: dt.datetime
    completed_at: dt.datetime | None


class SubnetScanDetailRead(SubnetScanRead):
    hosts: list[SubnetScanHostRead]


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=128)
    display_name: str | None = Field(None, max_length=255)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=64)
    kind: str = Field(default="person", max_length=32)
    notes: str | None = None

    @field_validator("username")
    @classmethod
    def username_strip(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("username kan ikke være tom")
        return s


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str | None
    email: str | None
    phone: str | None
    kind: str
    notes: str | None
    created_at: dt.datetime


class Ipv4AddressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    site_id: int
    ipv4_prefix_id: int | None
    address: str
    status: str
    owner_user_id: int | None
    note: str | None
    mac_address: str | None
    last_seen_at: dt.datetime | None
    device_type_id: int | None
    device_model_id: int | None
    device_id: int | None
    interface_id: int | None
    # Navn fra DCIM (dcim_device_interfaces.name), f.eks. me0.0 — ikke DB-kolonne.
    interface_name: str | None = None
    interface_ip_assignment_id: int | None
    created_at: dt.datetime
    updated_at: dt.datetime


class PrefixAddressGridRow(BaseModel):
    """Én rad i subnett-tabellen: inventory + DCIM-tildeling + siste skann per IP."""

    address: str
    inventory: Ipv4AddressRead | None = None
    assignment: Ipv4AssignmentInPrefixRead | None = None
    scan_ping_responded: bool | None = Field(
        default=None,
        description="True/False fra aktivt eller siste skann; None hvis ingen rad ennå under pågående skann",
    )
    scan_mac: str | None = None


class PrefixAddressGridRead(BaseModel):
    prefix_id: int
    cidr: str
    active_scan: SubnetScanRead | None = Field(
        default=None,
        description="Siste skann for prefikset (pending/running/completed/failed)",
    )
    rows: list[PrefixAddressGridRow]


class Ipv4AddressEnsure(BaseModel):
    ipv4_prefix_id: int = Field(..., ge=1)
    address: str = Field(..., min_length=1, max_length=45)


class Ipv4AddressPatch(BaseModel):
    status: str | None = Field(None, max_length=32)
    owner_user_id: int | None = Field(default=None)
    note: str | None = None
    mac_address: str | None = Field(None, max_length=32)
    device_type_id: int | None = Field(default=None)
    device_model_id: int | None = Field(default=None)
    device_id: int | None = Field(default=None)
    interface_id: int | None = Field(default=None)

    @field_validator("owner_user_id", "device_type_id", "device_model_id", "device_id", "interface_id")
    @classmethod
    def positive_id(cls, v: int | None) -> int | None:
        if v is not None and v < 1:
            raise ValueError("må være >= 1")
        return v


class Ipv4AddressRequest(BaseModel):
    ipv4_prefix_id: int = Field(..., ge=1)
    mode: str = Field(..., description="reserve | assign")
    interface_id: int | None = Field(None, ge=1)
    owner_user_id: int | None = Field(None, ge=1)
    note: str | None = None
    device_type_id: int | None = Field(None, ge=1)
    device_model_id: int | None = Field(None, ge=1)
    device_id: int | None = Field(None, ge=1)

    @field_validator("mode")
    @classmethod
    def mode_valid(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in ("reserve", "assign"):
            raise ValueError("mode må være reserve eller assign")
        return s
