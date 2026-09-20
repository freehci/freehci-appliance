"""Pydantic-skjemaer for federation API."""

from __future__ import annotations

import datetime as dt
from typing import Any

from pydantic import BaseModel, Field


class FederationHelloRead(BaseModel):
    instance_uuid: str
    name: str


class FederationPairingCreated(BaseModel):
    token: str
    instance_uuid: str
    name: str
    expires_at: dt.datetime


class FederationConnectIn(BaseModel):
    base_url: str = Field(..., min_length=8, max_length=512)
    pairing_token: str = Field(..., min_length=8, max_length=255)
    advertised_base_url: str | None = Field(None, max_length=512)


class FederationAcceptPeerIn(BaseModel):
    pairing_token: str
    instance_uuid: str
    name: str
    base_url: str


class FederationAcceptPeerRead(BaseModel):
    instance_uuid: str
    name: str
    token: str


class FederationPeerRead(BaseModel):
    id: int
    instance_uuid: str
    name: str
    base_url: str
    status: str
    last_seen_at: dt.datetime | None


class FederationTenantRoleRead(BaseModel):
    tenant_id: int
    tenant_slug: str
    tenant_name: str
    primary_instance_uuid: str
    is_primary_here: bool
    frozen: bool
    last_pull_at: dt.datetime | None


class FederationStatusRead(BaseModel):
    instance_uuid: str
    name: str
    peers: list[FederationPeerRead]
    tenants: list[FederationTenantRoleRead]


class FederationPullIn(BaseModel):
    tenant_slug: str
    peer_id: int | None = None


class FederationPullRead(BaseModel):
    tenant_slug: str
    checksum: str
    applied: bool
    primary_instance_uuid: str


class FederationConsistencyRead(BaseModel):
    tenant_slug: str
    checksum: str
    peer_checksum: str | None = None
    match: bool | None = None
    frozen: bool
    is_primary_here: bool


class FederationPromoteIn(BaseModel):
    tenant_slug: str
    peer_id: int | None = None


class FederationPromoteRead(BaseModel):
    tenant_slug: str
    primary_instance_uuid: str
    checksum: str
    match: bool = True


class FederationSnapshotRead(BaseModel):
    apiVersion: str
    kind: str
    checksum: str
    document: dict[str, Any]


class FederationFreezeIn(BaseModel):
    frozen: bool = True


class FederationHandoffIn(BaseModel):
    primary_instance_uuid: str = Field(..., min_length=36, max_length=36)
