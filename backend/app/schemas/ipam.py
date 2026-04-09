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
