"""Skjemaer for IPAM API (IPv4 prefiks per site)."""

from __future__ import annotations

import datetime as dt
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_CIRCUIT_TYPES = frozenset({"fiber", "vpn", "radio", "leased_line", "other"})


class Ipv4PrefixCreate(BaseModel):
    site_id: int
    name: str = Field(..., min_length=1, max_length=255)
    cidr: str = Field(..., min_length=1, max_length=32)
    description: str | None = None
    subnet_services: dict[str, Any] | None = None
    tenant_id: int | None = Field(None, ge=1, description="Valgfritt: kunde-/colo-tenant for prefikset")
    vlan_id: int | None = Field(None, ge=1, description="Valgfritt: VLAN (må tilhøre samme site)")
    vrf_id: int | None = Field(None, ge=1, description="Valgfritt: VRF (må tilhøre samme site)")

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
    subnet_services: dict[str, Any] | None = None
    tenant_id: int | None = None
    vlan_id: int | None = None
    vrf_id: int | None = None

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
    tenant_id: int | None = None
    vlan_id: int | None = None
    vrf_id: int | None = None
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
    subnet_services: dict[str, Any] | None = Field(
        default=None,
        description="Valgfritt: gateway, DNS, DHCP-server m.m. (JSON for integrasjoner)",
    )


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
    external_subject_id: str | None = Field(None, max_length=512)
    identity_provider: str | None = Field(None, max_length=128)

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
    external_subject_id: str | None = None
    identity_provider: str | None = None
    created_at: dt.datetime


class UserPatch(BaseModel):
    display_name: str | None = None
    email: str | None = None
    phone: str | None = None
    kind: str | None = Field(None, max_length=32)
    notes: str | None = None
    external_subject_id: str | None = Field(None, max_length=512)
    identity_provider: str | None = Field(None, max_length=128)


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
    address_role: str | None = Field(
        default=None,
        description="network | broadcast | host (IPv4; None for ukjent)",
    )
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


class Ipv4AddressBatchRequest(BaseModel):
    """Reserver eller tildel flere adresser; foretrukne prøves først."""

    ipv4_prefix_id: int = Field(..., ge=1)
    mode: str = Field(..., description="reserve | assign")
    count: int = Field(1, ge=1, le=256)
    preferred_addresses: list[str] = Field(default_factory=list)
    interface_id: int | None = Field(None, ge=1)
    owner_user_id: int | None = Field(None, ge=1)
    note: str | None = None
    device_type_id: int | None = Field(None, ge=1)
    device_model_id: int | None = Field(None, ge=1)
    device_id: int | None = Field(None, ge=1)

    @field_validator("mode")
    @classmethod
    def mode_valid_batch(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in ("reserve", "assign"):
            raise ValueError("mode må være reserve eller assign")
        return s

    @field_validator("preferred_addresses")
    @classmethod
    def cap_preferred(cls, v: list[str]) -> list[str]:
        if len(v) > 256:
            raise ValueError("høyst 256 foretrukne adresser")
        return v

    @model_validator(mode="after")
    def assign_only_one(self) -> Ipv4AddressBatchRequest:
        if self.mode == "assign" and self.count > 1:
            raise ValueError("mode=assign støtter bare count=1")
        return self


class Ipv4AddressBatchRead(BaseModel):
    addresses: list[Ipv4AddressRead]
    requested_count: int
    allocated_count: int


# --- VRF / VLAN / samband (circuits) ---


class IpamVrfCreate(BaseModel):
    site_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=128)
    route_distinguisher: str | None = Field(None, max_length=64)
    description: str | None = None


class IpamVrfRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    site_id: int
    name: str
    route_distinguisher: str | None
    description: str | None
    created_at: dt.datetime


class IpamVlanCreate(BaseModel):
    site_id: int = Field(..., ge=1)
    vid: int = Field(..., ge=1, le=4094)
    name: str = Field(..., min_length=1, max_length=255)
    vrf_id: int | None = None
    description: str | None = None
    tenant_id: int | None = Field(None, ge=1)


class IpamVlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    site_id: int
    tenant_id: int | None = None
    vid: int
    name: str
    vrf_id: int | None
    description: str | None
    created_at: dt.datetime


class IpamCircuitCreate(BaseModel):
    tenant_id: int = Field(..., ge=1)
    circuit_number: str = Field(..., min_length=1, max_length=128)
    name: str = Field(..., min_length=1, max_length=255)
    circuit_type: str = Field(..., min_length=1, max_length=32)
    description: str | None = None
    is_leased: bool = False
    provider_name: str | None = Field(None, max_length=255)
    established_on: dt.date | None = None
    contract_end_on: dt.date | None = None

    @field_validator("circuit_type")
    @classmethod
    def circuit_type_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in _CIRCUIT_TYPES:
            raise ValueError(f"circuit_type må være en av: {', '.join(sorted(_CIRCUIT_TYPES))}")
        return s


class IpamCircuitUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    circuit_type: str | None = Field(None, min_length=1, max_length=32)
    is_leased: bool | None = None
    provider_name: str | None = Field(None, max_length=255)
    established_on: dt.date | None = None
    contract_end_on: dt.date | None = None

    @field_validator("circuit_type")
    @classmethod
    def circuit_type_ok(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if s not in _CIRCUIT_TYPES:
            raise ValueError(f"circuit_type må være en av: {', '.join(sorted(_CIRCUIT_TYPES))}")
        return s


class IpamCircuitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    circuit_number: str
    name: str
    description: str | None
    circuit_type: str
    is_leased: bool
    provider_name: str | None
    established_on: dt.date | None
    contract_end_on: dt.date | None
    created_at: dt.datetime


class IpamCircuitTerminationCreate(BaseModel):
    endpoint: Literal["a", "z"]
    interface_id: int | None = Field(None, ge=1)
    label: str | None = Field(None, max_length=255)


class IpamCircuitTerminationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    circuit_id: int
    endpoint: str
    interface_id: int | None
    label: str | None
