"""Skjemaer for IPAM API (IPv4 prefiks per site)."""

from __future__ import annotations

import datetime as dt
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.asn import normalize_asn
from app.core.route_distinguisher import normalize_route_distinguisher, normalize_route_target
from app.core.secret_ref import normalize_secret_ref

BGP_ADDRESS_FAMILIES = frozenset({"ipv4-unicast", "ipv6-unicast", "evpn"})
BGP_DESIRED_STATUSES = frozenset({"planned", "active", "disabled"})
BGP_OBSERVED_STATUSES = frozenset({"idle", "connect", "established", "admin-down"})

_CIRCUIT_TYPES = frozenset({"fiber", "vpn", "wireguard", "radio", "leased_line", "other"})
TRANSPORT_CIRCUIT_TYPES = frozenset({"fiber", "radio", "leased_line"})
CLASSIFY_CIRCUIT_TYPES = frozenset({"vpn", "wireguard", "other"})
CIRCUIT_LAYERS = frozenset({"transport", "overlay"})
VPN_TYPES = frozenset({"wireguard", "ipsec", "other"})
TUNNEL_STATUSES = frozenset({"planned", "active", "deprecated"})
_OVERLAP_POLICIES = frozenset({"site-local", "global-unique"})
_OWNER_TYPES = frozenset({"user", "token", "cluster", "system"})
ADDRESS_STATUSES = frozenset({"planned", "reserved", "assigned", "dhcp", "discovered", "deprecated"})
_ADDRESS_STATUSES = ADDRESS_STATUSES
_ADDRESS_MODES = frozenset({"reserve", "assign"})
_ADDRESS_ROLES = frozenset({"gateway", "vip", "anycast", "lb", "host", "dhcp", "reserved"})
PREFIX_ROLES = frozenset(
    {"container", "access", "overlay-pod", "overlay-service", "lb-pool", "p2p"},
)
# GitOps/eldre klienter sendte livsløp som rolle.
PREFIX_ROLE_ALIASES = {"active": "access", "reserved": "container"}
PREFIX_STATUSES = frozenset({"planned", "active", "reserved", "deprecated"})
NO_HOST_ALLOC_ROLES = frozenset({"container", "overlay-pod", "overlay-service"})
NO_VLAN_ROLES = frozenset({"container", "overlay-pod", "overlay-service", "p2p"})
NO_HOST_ALLOC_STATUSES = frozenset({"reserved", "deprecated"})
IPV4_RANGE_KINDS = frozenset({"allocation", "reserved", "dhcp", "other"})
VRF_INSTANCE_INTENTS = frozenset({"recorded", "intended"})
ROUTE_TARGET_DIRECTIONS = frozenset({"import", "export"})


def _csv_or_list(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        return [p.strip() for p in v.split(",") if p.strip()]
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    return [str(v).strip()] if str(v).strip() else []


class DhcpRange(BaseModel):
    start: str
    end: str


class SubnetServices(BaseModel):
    """Typet kontrakt for gateway/DNS/DHCP — gamle streng-verdier normaliseres til lister."""

    model_config = ConfigDict(extra="ignore")

    gateway: str | None = None
    dns: list[str] = Field(default_factory=list)
    ntp: list[str] = Field(default_factory=list)
    dhcp_server: str | None = None
    dhcp_range: DhcpRange | None = None
    domain: str | None = None
    mtu: int | None = Field(None, ge=576, le=9216)

    @field_validator("dns", "ntp", mode="before")
    @classmethod
    def split_servers(cls, v: Any) -> list[str]:
        return _csv_or_list(v)

    @field_validator("gateway", "dhcp_server", "domain")
    @classmethod
    def strip_opt(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        return s or None


def parse_subnet_services(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    return SubnetServices.model_validate(raw).model_dump()


def _role_ok(v: str | None, allowed: frozenset[str], label: str) -> str | None:
    if v is None:
        return None
    s = v.strip().lower()
    alias = PREFIX_ROLE_ALIASES.get(s)
    if alias is not None and alias in allowed:
        s = alias
    if s not in allowed:
        raise ValueError(f"{label} må være en av: {', '.join(sorted(allowed))}")
    return s


class Ipv4PrefixCreate(BaseModel):
    site_id: int
    name: str = Field(..., min_length=1, max_length=255)
    cidr: str = Field(..., min_length=1, max_length=32)
    slug: str | None = Field(None, min_length=1, max_length=128, description="Stabil nøkkel; genereres fra name hvis utelatt")
    role: str = Field("access", description="container | access | overlay-pod | overlay-service | lb-pool | p2p")
    status: str = Field("active", description="planned | active | reserved | deprecated")
    description: str | None = None
    subnet_services: SubnetServices | dict[str, Any] | None = None
    tenant_id: int | None = Field(None, ge=1, description="Valgfritt: kunde-/colo-tenant for prefikset")
    vlan_id: int | None = Field(None, ge=1, description="Valgfritt: VLAN (må tilhøre samme site)")
    vrf_id: int | None = Field(None, ge=1, description="Valgfritt: VRF (må tilhøre samme site)")
    overlap_policy: str | None = Field(None, description="site-local | global-unique; overlay/p2p default global-unique")
    dual_stack_group_id: int | None = Field(None, ge=1)

    @field_validator("cidr")
    @classmethod
    def cidr_not_empty(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("cidr kan ikke være tom")
        return s

    @field_validator("slug")
    @classmethod
    def slug_strip(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if not s:
            raise ValueError("slug kan ikke være tom")
        return s

    @field_validator("role")
    @classmethod
    def role_ok(cls, v: str) -> str:
        return _role_ok(v, PREFIX_ROLES, "role") or "access"

    @field_validator("status")
    @classmethod
    def status_ok(cls, v: str) -> str:
        return _role_ok(v, PREFIX_STATUSES, "status") or "active"

    @field_validator("overlap_policy")
    @classmethod
    def overlap_ok(cls, v: str | None) -> str | None:
        return _role_ok(v, _OVERLAP_POLICIES, "overlap_policy")


class Ipv4PrefixEnsure(BaseModel):
    """Idempotent opprett/hent prefiks på (site, vrf, cidr). site_id eller site_slug kreves."""

    site_id: int | None = Field(None, ge=1)
    site_slug: str | None = Field(None, max_length=64)
    cidr: str = Field(..., min_length=1, max_length=32)
    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=128)
    role: str | None = None
    status: str | None = None
    description: str | None = None
    subnet_services: SubnetServices | dict[str, Any] | None = None
    tenant_id: int | None = Field(None, ge=1)
    tenant_slug: str | None = Field(None, max_length=64)
    vlan_id: int | None = Field(None, ge=1)
    vlan_slug: str | None = Field(None, max_length=128)
    vrf_id: int | None = Field(None, ge=1)
    vrf_slug: str | None = Field(None, max_length=128)
    overlap_policy: str | None = None
    dual_stack_group_id: int | None = Field(None, ge=1)

    @model_validator(mode="after")
    def site_ref_present(self) -> Ipv4PrefixEnsure:
        if self.site_id is None and not (self.site_slug or "").strip():
            raise ValueError("site_id eller site_slug kreves")
        return self

    @field_validator("cidr")
    @classmethod
    def cidr_not_empty(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("cidr kan ikke være tom")
        return s

    @field_validator("slug")
    @classmethod
    def slug_strip(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if not s:
            raise ValueError("slug kan ikke være tom")
        return s

    @field_validator("role")
    @classmethod
    def role_ok_ens(cls, v: str | None) -> str | None:
        return _role_ok(v, PREFIX_ROLES, "role")

    @field_validator("status")
    @classmethod
    def status_ok_ens(cls, v: str | None) -> str | None:
        return _role_ok(v, PREFIX_STATUSES, "status")

    @field_validator("overlap_policy")
    @classmethod
    def overlap_ok_ens(cls, v: str | None) -> str | None:
        return _role_ok(v, _OVERLAP_POLICIES, "overlap_policy")


class Ipv4PrefixUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=128)
    cidr: str | None = Field(None, min_length=1, max_length=32)
    role: str | None = None
    status: str | None = None
    description: str | None = None
    subnet_services: SubnetServices | dict[str, Any] | None = None
    tenant_id: int | None = None
    vlan_id: int | None = None
    vrf_id: int | None = None
    overlap_policy: str | None = None
    dual_stack_group_id: int | None = Field(None, ge=1)

    @field_validator("cidr")
    @classmethod
    def cidr_strip(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if not s:
            raise ValueError("cidr kan ikke være tom")
        return s

    @field_validator("slug")
    @classmethod
    def slug_strip(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if not s:
            raise ValueError("slug kan ikke være tom")
        return s

    @field_validator("role")
    @classmethod
    def role_ok_up(cls, v: str | None) -> str | None:
        return _role_ok(v, PREFIX_ROLES, "role")

    @field_validator("status")
    @classmethod
    def status_ok_up(cls, v: str | None) -> str | None:
        return _role_ok(v, PREFIX_STATUSES, "status")

    @field_validator("overlap_policy")
    @classmethod
    def overlap_ok_up(cls, v: str | None) -> str | None:
        return _role_ok(v, _OVERLAP_POLICIES, "overlap_policy")


class Ipv4RangeCreate(BaseModel):
    """Inventory-vindu inne i et prefiks. Ikke DHCP-scope, lease eller DNS."""

    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=128)
    kind: str = Field("allocation", description="allocation | reserved | dhcp | other")
    start_address: str = Field(..., min_length=1, max_length=45)
    end_address: str = Field(..., min_length=1, max_length=45)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("name kan ikke være tom")
        return s

    @field_validator("slug")
    @classmethod
    def slug_strip(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if not s:
            raise ValueError("slug kan ikke være tom")
        return s

    @field_validator("kind")
    @classmethod
    def kind_ok(cls, v: str) -> str:
        return _role_ok(v, IPV4_RANGE_KINDS, "kind") or "allocation"

    @field_validator("start_address", "end_address")
    @classmethod
    def addr_strip(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("adresse kan ikke være tom")
        return s


class Ipv4RangeUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=128)
    kind: str | None = None
    start_address: str | None = Field(None, min_length=1, max_length=45)
    end_address: str | None = Field(None, min_length=1, max_length=45)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def name_strip_up(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if not s:
            raise ValueError("name kan ikke være tom")
        return s

    @field_validator("slug")
    @classmethod
    def slug_strip_up(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if not s:
            raise ValueError("slug kan ikke være tom")
        return s

    @field_validator("kind")
    @classmethod
    def kind_ok_up(cls, v: str | None) -> str | None:
        return _role_ok(v, IPV4_RANGE_KINDS, "kind")

    @field_validator("start_address", "end_address")
    @classmethod
    def addr_strip_up(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if not s:
            raise ValueError("adresse kan ikke være tom")
        return s


class Ipv4RangeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ipv4_prefix_id: int
    name: str
    slug: str
    kind: str
    start_address: str
    end_address: str
    description: str | None = None
    created_at: dt.datetime
    updated_at: dt.datetime | None = None


class Ipv4PrefixRead(BaseModel):
    """Returneres fra tjenestelaget med telling fra inventory + DCIM."""

    id: int
    site_id: int
    tenant_id: int | None = None
    vlan_id: int | None = None
    vrf_id: int | None = None
    name: str
    slug: str
    role: str = "access"
    status: str = "active"
    cidr: str
    description: str | None
    created_at: dt.datetime
    updated_at: dt.datetime | None = None
    parent_id: int | None = None
    used_count: int = Field(
        description=(
            "Unike IPv4-adresser i CIDR som er inventory reserved|assigned "
            "eller DCIM-tildelt på samme site"
        ),
    )
    address_total: int = Field(description="Totalt antall IPv4-adresser i CIDR (inkl. nettverk/broadcast der relevant)")
    usable_hosts: int = Field(0, description="Adresser som kan tildeles (hopper over net/bcast)")
    utilization: float = Field(0, description="used_count / usable_hosts")
    created: bool | None = Field(None, description="Satt av ensure: true hvis raden ble opprettet i dette kallet")
    subnet_services: dict[str, Any] | None = Field(
        default=None,
        description="Typet: gateway, dns[], ntp[], dhcp_server, dhcp_range, domain, mtu",
    )
    overlap_policy: str = "site-local"
    dual_stack_group_id: int | None = None
    etag: str | None = Field(None, description="Optimistic concurrency; send som If-Match på PATCH/DELETE")


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
    ipv4_prefix_id: int | None = Field(None, ge=1)
    ipv6_prefix_id: int | None = Field(None, ge=1)

    @model_validator(mode="after")
    def one_family(self) -> SubnetScanCreate:
        if (self.ipv4_prefix_id is None) == (self.ipv6_prefix_id is None):
            raise ValueError("oppgi nøyaktig én av ipv4_prefix_id eller ipv6_prefix_id")
        return self


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
    ipv6_prefix_id: int | None = None
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
    avatar_file: str | None = None
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
    role: str = "host"
    hostname: str | None = None
    fqdn: str | None = None
    dns_name: str | None = None
    created: bool | None = None
    owner_user_id: int | None
    owner_type: str | None = None
    owner_ref: str | None = None
    expires_at: dt.datetime | None = None
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
    virtual_interface_id: int | None = None
    created_at: dt.datetime
    updated_at: dt.datetime
    etag: str | None = Field(None, description="Optimistic concurrency; send som If-Match på PATCH/DELETE/release")


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
    ipv4_prefix_id: int | None = Field(None, ge=1)
    prefix_cidr: str | None = Field(None, max_length=32)
    site_id: int | None = Field(None, ge=1)
    site_slug: str | None = Field(None, max_length=64)
    address: str = Field(..., min_length=1, max_length=45)
    mode: str | None = Field(None, description="reserve | assign — overstyrer status hvis satt")
    status: str | None = Field(None, description="planned | reserved | assigned | dhcp | discovered | deprecated")
    note: str | None = None
    owner_user_id: int | None = Field(None, ge=1)
    device_type_id: int | None = Field(None, ge=1)
    device_model_id: int | None = Field(None, ge=1)
    device_id: int | None = Field(None, ge=1)
    interface_id: int | None = Field(None, ge=1)
    role: str | None = None
    hostname: str | None = Field(None, max_length=255)
    fqdn: str | None = Field(None, max_length=255)
    dns_name: str | None = Field(None, max_length=255)

    @field_validator("mode")
    @classmethod
    def mode_valid(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if s not in _ADDRESS_MODES:
            raise ValueError("mode må være reserve eller assign")
        return s

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if s not in _ADDRESS_STATUSES:
            raise ValueError("ugyldig status")
        return s

    @field_validator("role")
    @classmethod
    def role_ok_ens_addr(cls, v: str | None) -> str | None:
        return _role_ok(v, _ADDRESS_ROLES, "role")

    @model_validator(mode="after")
    def prefix_ref_present(self) -> Ipv4AddressEnsure:
        if self.ipv4_prefix_id is None and not (self.prefix_cidr or "").strip():
            raise ValueError("ipv4_prefix_id eller prefix_cidr kreves")
        return self


class Ipv4AddressPatch(BaseModel):
    status: str | None = Field(None, max_length=32)
    role: str | None = None
    hostname: str | None = Field(None, max_length=255)
    fqdn: str | None = Field(None, max_length=255)
    dns_name: str | None = Field(None, max_length=255)
    owner_user_id: int | None = Field(default=None)
    note: str | None = None
    mac_address: str | None = Field(None, max_length=32)
    device_type_id: int | None = Field(default=None)
    device_model_id: int | None = Field(default=None)
    device_id: int | None = Field(default=None)
    interface_id: int | None = Field(default=None)

    @field_validator("status")
    @classmethod
    def status_valid_patch(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if s not in _ADDRESS_STATUSES:
            raise ValueError("ugyldig status")
        return s

    @field_validator("role")
    @classmethod
    def role_ok_patch_addr(cls, v: str | None) -> str | None:
        return _role_ok(v, _ADDRESS_ROLES, "role")

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
    role: str | None = None

    @field_validator("mode")
    @classmethod
    def mode_valid(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in ("reserve", "assign"):
            raise ValueError("mode må være reserve eller assign")
        return s

    @field_validator("role")
    @classmethod
    def role_ok_req(cls, v: str | None) -> str | None:
        return _role_ok(v, _ADDRESS_ROLES, "role")


class Ipv4AddressBind(BaseModel):
    device_id: int = Field(..., ge=1)
    interface_id: int | None = Field(None, ge=1)


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
    role: str | None = None

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

    @field_validator("role")
    @classmethod
    def role_ok_batch(cls, v: str | None) -> str | None:
        return _role_ok(v, _ADDRESS_ROLES, "role")

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
    slug: str | None = Field(None, min_length=1, max_length=128)
    route_distinguisher: str | None = Field(None, max_length=64, description="ASN:nn eller IPv4:nn")
    description: str | None = None

    @field_validator("route_distinguisher")
    @classmethod
    def rd_ok(cls, v: str | None) -> str | None:
        return normalize_route_distinguisher(v)


class IpamVrfUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    slug: str | None = Field(None, min_length=1, max_length=128)
    route_distinguisher: str | None = Field(None, max_length=64)
    description: str | None = None

    @field_validator("route_distinguisher")
    @classmethod
    def rd_ok_up(cls, v: str | None) -> str | None:
        return normalize_route_distinguisher(v)


class IpamVrfEnsure(IpamVrfCreate):
    pass


class IpamVrfRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    site_id: int
    name: str
    slug: str
    route_distinguisher: str | None
    description: str | None
    created: bool | None = None
    created_at: dt.datetime


class IpamRouteTargetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    slug: str | None = Field(None, min_length=1, max_length=128)
    value: str = Field(..., min_length=1, max_length=64, description="ASN:nn eller IPv4:nn — ikke RD")
    description: str | None = None

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("name kan ikke være tom")
        return s

    @field_validator("slug")
    @classmethod
    def slug_strip(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if not s:
            raise ValueError("slug kan ikke være tom")
        return s

    @field_validator("value")
    @classmethod
    def value_ok(cls, v: str) -> str:
        out = normalize_route_target(v)
        if out is None:
            raise ValueError("RT-verdi kreves")
        return out


class IpamRouteTargetUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    slug: str | None = Field(None, min_length=1, max_length=128)
    value: str | None = Field(None, min_length=1, max_length=64)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def name_strip_up(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip()
        if not s:
            raise ValueError("name kan ikke være tom")
        return s

    @field_validator("slug")
    @classmethod
    def slug_strip_up(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if not s:
            raise ValueError("slug kan ikke være tom")
        return s

    @field_validator("value")
    @classmethod
    def value_ok_up(cls, v: str | None) -> str | None:
        if v is None:
            return None
        out = normalize_route_target(v)
        if out is None:
            raise ValueError("RT-verdi kreves")
        return out


class IpamRouteTargetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    value: str
    description: str | None
    created_at: dt.datetime


class IpamVrfRouteTargetCreate(BaseModel):
    route_target_id: int = Field(..., ge=1)
    direction: str = Field(..., description="import | export")

    @field_validator("direction")
    @classmethod
    def dir_ok(cls, v: str) -> str:
        return _role_ok(v, ROUTE_TARGET_DIRECTIONS, "direction") or "import"


class IpamVrfRouteTargetRead(BaseModel):
    id: int
    vrf_id: int
    vrf_name: str
    vrf_slug: str
    route_target_id: int
    route_target_slug: str
    route_target_name: str
    value: str
    direction: str


class IpamVrfInstanceCreate(BaseModel):
    """Registrer logisk VRF på en enhet. Påfører ikke config, RT eller RIB."""

    device_id: int = Field(..., ge=1)
    slug: str | None = Field(None, min_length=1, max_length=128)
    intent: str = Field("recorded", description="recorded | intended")
    route_distinguisher: str | None = Field(None, max_length=64, description="Valgfri RD på instansen; tom arver fra VRF")
    description: str | None = None

    @field_validator("slug")
    @classmethod
    def slug_strip(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if not s:
            raise ValueError("slug kan ikke være tom")
        return s

    @field_validator("intent")
    @classmethod
    def intent_ok(cls, v: str) -> str:
        return _role_ok(v, VRF_INSTANCE_INTENTS, "intent") or "recorded"

    @field_validator("route_distinguisher")
    @classmethod
    def rd_ok(cls, v: str | None) -> str | None:
        return normalize_route_distinguisher(v)


class IpamVrfInstanceUpdate(BaseModel):
    slug: str | None = Field(None, min_length=1, max_length=128)
    intent: str | None = None
    route_distinguisher: str | None = Field(None, max_length=64)
    description: str | None = None

    @field_validator("slug")
    @classmethod
    def slug_strip_up(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if not s:
            raise ValueError("slug kan ikke være tom")
        return s

    @field_validator("intent")
    @classmethod
    def intent_ok_up(cls, v: str | None) -> str | None:
        return _role_ok(v, VRF_INSTANCE_INTENTS, "intent")

    @field_validator("route_distinguisher")
    @classmethod
    def rd_ok_up(cls, v: str | None) -> str | None:
        return normalize_route_distinguisher(v)


class IpamVrfInstanceRead(BaseModel):
    id: int
    vrf_id: int
    vrf_name: str
    vrf_slug: str
    device_id: int
    device_name: str
    slug: str
    intent: str
    route_distinguisher: str | None
    effective_rd: str | None = Field(None, description="Instans-RD hvis satt, ellers VRF-RD")
    description: str | None
    created_at: dt.datetime


class IpamAutonomousSystemCreate(BaseModel):
    asn: int
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    tenant_id: int | None = Field(None, ge=1)
    description: str | None = None

    @field_validator("asn")
    @classmethod
    def asn_ok(cls, v: int) -> int:
        return normalize_asn(v)


class IpamAutonomousSystemUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    tenant_id: int | None = Field(None, ge=1)
    description: str | None = None


class IpamAutonomousSystemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asn: int
    name: str
    slug: str
    is_private: bool
    tenant_id: int | None
    description: str | None
    created_at: dt.datetime


class IpamAsAssignmentCreate(BaseModel):
    autonomous_system_id: int = Field(..., ge=1)
    site_id: int = Field(..., ge=1)
    vrf_id: int | None = Field(None, ge=1)


class IpamAsAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    autonomous_system_id: int
    site_id: int
    vrf_id: int | None
    asn: int | None = None
    as_name: str | None = None
    site_name: str | None = None
    vrf_name: str | None = None
    created_at: dt.datetime


class IpamBgpSessionCreate(BaseModel):
    site_id: int = Field(..., ge=1)
    local_as_id: int = Field(..., ge=1)
    remote_as_id: int | None = Field(None, ge=1)
    remote_asn: int | None = None
    peer_ip: str = Field(..., min_length=1, max_length=64)
    vrf_id: int | None = Field(None, ge=1)
    name: str | None = Field(None, max_length=255)
    slug: str | None = Field(None, max_length=128)
    address_families: list[str] = Field(default_factory=lambda: ["ipv4-unicast"])
    desired_status: str = "planned"
    observed_status: str | None = None
    local_device_id: int | None = Field(None, ge=1)
    local_interface_id: int | None = Field(None, ge=1)
    description: str | None = None

    @field_validator("remote_asn")
    @classmethod
    def remote_asn_ok(cls, v: int | None) -> int | None:
        if v is None:
            return None
        return normalize_asn(v)

    @field_validator("address_families", mode="before")
    @classmethod
    def families_ok(cls, v: Any) -> list[str]:
        items = _csv_or_list(v)
        if not items:
            return ["ipv4-unicast"]
        out: list[str] = []
        seen: set[str] = set()
        for raw in items:
            s = raw.strip().lower()
            if s not in BGP_ADDRESS_FAMILIES:
                raise ValueError(f"address family må være en av: {', '.join(sorted(BGP_ADDRESS_FAMILIES))}")
            if s not in seen:
                seen.add(s)
                out.append(s)
        return out

    @field_validator("desired_status")
    @classmethod
    def desired_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in BGP_DESIRED_STATUSES:
            raise ValueError(f"desired_status må være en av: {', '.join(sorted(BGP_DESIRED_STATUSES))}")
        return s

    @field_validator("observed_status")
    @classmethod
    def observed_ok(cls, v: str | None) -> str | None:
        if v is None or not str(v).strip():
            return None
        s = str(v).strip().lower()
        if s not in BGP_OBSERVED_STATUSES:
            raise ValueError(f"observed_status må være en av: {', '.join(sorted(BGP_OBSERVED_STATUSES))}")
        return s

    @field_validator("peer_ip")
    @classmethod
    def peer_ip_ok(cls, v: str) -> str:
        import ipaddress

        s = v.strip()
        try:
            return str(ipaddress.ip_address(s))
        except ValueError as e:
            raise ValueError("peer_ip må være en IPv4- eller IPv6-adresse") from e


class IpamBgpSessionUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    slug: str | None = Field(None, max_length=128)
    remote_as_id: int | None = Field(None, ge=1)
    remote_asn: int | None = None
    peer_ip: str | None = Field(None, min_length=1, max_length=64)
    vrf_id: int | None = Field(None, ge=1)
    address_families: list[str] | None = None
    desired_status: str | None = None
    observed_status: str | None = None
    local_device_id: int | None = Field(None, ge=1)
    local_interface_id: int | None = Field(None, ge=1)
    description: str | None = None

    @field_validator("remote_asn")
    @classmethod
    def remote_asn_ok(cls, v: int | None) -> int | None:
        if v is None:
            return None
        return normalize_asn(v)

    @field_validator("address_families", mode="before")
    @classmethod
    def families_ok(cls, v: Any) -> list[str] | None:
        if v is None:
            return None
        items = _csv_or_list(v)
        out: list[str] = []
        seen: set[str] = set()
        for raw in items:
            s = raw.strip().lower()
            if s not in BGP_ADDRESS_FAMILIES:
                raise ValueError(f"address family må være en av: {', '.join(sorted(BGP_ADDRESS_FAMILIES))}")
            if s not in seen:
                seen.add(s)
                out.append(s)
        return out or None

    @field_validator("desired_status")
    @classmethod
    def desired_ok(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if s not in BGP_DESIRED_STATUSES:
            raise ValueError(f"desired_status må være en av: {', '.join(sorted(BGP_DESIRED_STATUSES))}")
        return s

    @field_validator("observed_status")
    @classmethod
    def observed_ok(cls, v: str | None) -> str | None:
        if v is None or not str(v).strip():
            return None
        s = str(v).strip().lower()
        if s not in BGP_OBSERVED_STATUSES:
            raise ValueError(f"observed_status må være en av: {', '.join(sorted(BGP_OBSERVED_STATUSES))}")
        return s

    @field_validator("peer_ip")
    @classmethod
    def peer_ip_ok(cls, v: str | None) -> str | None:
        if v is None:
            return None
        import ipaddress

        s = v.strip()
        try:
            return str(ipaddress.ip_address(s))
        except ValueError as e:
            raise ValueError("peer_ip må være en IPv4- eller IPv6-adresse") from e


class IpamBgpSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    site_id: int
    local_as_id: int
    remote_as_id: int | None
    remote_asn: int
    peer_ip: str
    vrf_id: int | None
    name: str
    slug: str
    address_families: list[str]
    desired_status: str
    observed_status: str | None
    local_device_id: int | None
    local_interface_id: int | None
    description: str | None
    created_at: dt.datetime


class IpamVlanGroupCreate(BaseModel):
    site_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=128)
    slug: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None


class IpamVlanGroupUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    slug: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None


class IpamVlanGroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    site_id: int
    name: str
    slug: str
    description: str | None
    created_at: dt.datetime


class IpamVlanCreate(BaseModel):
    site_id: int = Field(..., ge=1)
    vlan_group_id: int | None = Field(None, ge=1, description="Utelatt: sitens Default-gruppe")
    vid: int = Field(..., ge=1, le=4094)
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=128)
    vrf_id: int | None = None
    description: str | None = None
    tenant_id: int | None = Field(None, ge=1)


class IpamVlanUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=128)
    vlan_group_id: int | None = Field(None, ge=1)
    vrf_id: int | None = None
    description: str | None = None
    tenant_id: int | None = Field(None, ge=1)


class IpamVlanEnsure(IpamVlanCreate):
    pass


class IpamVlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    site_id: int
    vlan_group_id: int
    tenant_id: int | None = None
    vid: int
    name: str
    slug: str
    vrf_id: int | None
    description: str | None
    created: bool | None = None
    created_at: dt.datetime


class IpamCircuitCreate(BaseModel):
    tenant_id: int | None = Field(None, ge=1, description="Valgfri; intern WireGuard trenger ikke colo-tenant")
    circuit_number: str = Field(..., min_length=1, max_length=128)
    name: str = Field(..., min_length=1, max_length=255)
    circuit_type: str = Field(..., min_length=1, max_length=32)
    layer: str | None = Field(None, max_length=16)
    description: str | None = None
    is_leased: bool = False
    provider_name: str | None = Field(None, max_length=255)
    provider_id: int | None = Field(None, ge=1)
    provider_account_id: int | None = Field(None, ge=1)
    established_on: dt.date | None = None
    contract_end_on: dt.date | None = None
    a_site_id: int | None = Field(None, ge=1)
    z_site_id: int | None = Field(None, ge=1)

    @field_validator("circuit_type")
    @classmethod
    def circuit_type_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in _CIRCUIT_TYPES:
            raise ValueError(f"circuit_type må være en av: {', '.join(sorted(_CIRCUIT_TYPES))}")
        return s

    @field_validator("layer")
    @classmethod
    def layer_ok(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if not s:
            return None
        if s not in CIRCUIT_LAYERS:
            raise ValueError(f"layer må være en av: {', '.join(sorted(CIRCUIT_LAYERS))}")
        return s


class IpamCircuitUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    circuit_type: str | None = Field(None, min_length=1, max_length=32)
    layer: str | None = Field(None, max_length=16)
    is_leased: bool | None = None
    provider_name: str | None = Field(None, max_length=255)
    provider_id: int | None = Field(None, ge=1)
    provider_account_id: int | None = Field(None, ge=1)
    established_on: dt.date | None = None
    contract_end_on: dt.date | None = None
    tenant_id: int | None = Field(None, ge=1)
    a_site_id: int | None = Field(None, ge=1)
    z_site_id: int | None = Field(None, ge=1)

    @field_validator("circuit_type")
    @classmethod
    def circuit_type_ok(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if s not in _CIRCUIT_TYPES:
            raise ValueError(f"circuit_type må være en av: {', '.join(sorted(_CIRCUIT_TYPES))}")
        return s

    @field_validator("layer")
    @classmethod
    def layer_ok(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if not s:
            return None
        if s not in CIRCUIT_LAYERS:
            raise ValueError(f"layer må være en av: {', '.join(sorted(CIRCUIT_LAYERS))}")
        return s


class IpamCircuitClassify(BaseModel):
    layer: str = Field(..., min_length=1, max_length=16)
    create_vpn: bool = True

    @field_validator("layer")
    @classmethod
    def layer_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in CIRCUIT_LAYERS:
            raise ValueError(f"layer må være en av: {', '.join(sorted(CIRCUIT_LAYERS))}")
        return s


class IpamCircuitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int | None = None
    a_site_id: int | None = None
    z_site_id: int | None = None
    circuit_number: str
    name: str
    description: str | None
    circuit_type: str
    layer: str | None = None
    is_leased: bool
    provider_name: str | None
    provider_id: int | None = None
    provider_account_id: int | None = None
    needs_classification: bool = False
    established_on: dt.date | None
    contract_end_on: dt.date | None
    created_at: dt.datetime


class IpamCircuitClassifyRead(BaseModel):
    circuit: IpamCircuitRead
    vpn_service_id: int | None = None


class IpamCircuitTerminationCreate(BaseModel):
    endpoint: Literal["a", "z"]
    device_id: int | None = Field(None, ge=1)
    interface_id: int | None = Field(None, ge=1)
    site_id: int | None = Field(None, ge=1)
    label: str | None = Field(None, max_length=255)


class IpamCircuitTerminationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    circuit_id: int
    endpoint: str
    device_id: int | None = None
    interface_id: int | None
    site_id: int | None = None
    label: str | None
    device_name: str | None = None
    interface_name: str | None = None


class IpamProviderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    asn: int | None = Field(None, ge=1, le=4294967295)
    website: str | None = Field(None, max_length=255)
    description: str | None = None


class IpamProviderUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    asn: int | None = Field(None, ge=1, le=4294967295)
    website: str | None = Field(None, max_length=255)
    description: str | None = None


class IpamProviderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    asn: int | None
    website: str | None
    description: str | None
    created_at: dt.datetime


class IpamProviderAccountCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    tenant_id: int | None = Field(None, ge=1)
    account_number: str | None = Field(None, max_length=128)
    description: str | None = None


class IpamProviderAccountUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    tenant_id: int | None = Field(None, ge=1)
    account_number: str | None = Field(None, max_length=128)
    description: str | None = None


class IpamProviderAccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider_id: int
    tenant_id: int | None
    name: str
    slug: str
    account_number: str | None
    description: str | None
    created_at: dt.datetime


class IpamVpnServiceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    vpn_type: str = Field(..., min_length=1, max_length=32)
    tenant_id: int | None = Field(None, ge=1)
    source_circuit_id: int | None = Field(None, ge=1)
    description: str | None = None

    @field_validator("vpn_type")
    @classmethod
    def vpn_type_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in VPN_TYPES:
            raise ValueError(f"vpn_type må være en av: {', '.join(sorted(VPN_TYPES))}")
        return s


class IpamVpnServiceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    vpn_type: str | None = Field(None, min_length=1, max_length=32)
    tenant_id: int | None = Field(None, ge=1)
    source_circuit_id: int | None = Field(None, ge=1)
    description: str | None = None

    @field_validator("vpn_type")
    @classmethod
    def vpn_type_ok(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if s not in VPN_TYPES:
            raise ValueError(f"vpn_type må være en av: {', '.join(sorted(VPN_TYPES))}")
        return s


class IpamVpnServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int | None
    name: str
    slug: str
    vpn_type: str
    source_circuit_id: int | None
    description: str | None
    created_at: dt.datetime


class IpamTunnelProfileCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    vpn_type: str = Field(..., min_length=1, max_length=32)
    settings: dict[str, Any] | None = None
    description: str | None = None

    @field_validator("vpn_type")
    @classmethod
    def vpn_type_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in VPN_TYPES:
            raise ValueError(f"vpn_type må være en av: {', '.join(sorted(VPN_TYPES))}")
        return s


class IpamTunnelProfileUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    vpn_type: str | None = Field(None, min_length=1, max_length=32)
    settings: dict[str, Any] | None = None
    description: str | None = None

    @field_validator("vpn_type")
    @classmethod
    def vpn_type_ok(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if s not in VPN_TYPES:
            raise ValueError(f"vpn_type må være en av: {', '.join(sorted(VPN_TYPES))}")
        return s


class IpamTunnelProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    vpn_type: str
    settings: dict[str, Any] | None
    description: str | None
    created_at: dt.datetime


class IpamTunnelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    status: str = "planned"
    profile_id: int | None = Field(None, ge=1)
    description: str | None = None

    @field_validator("status")
    @classmethod
    def status_ok(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in TUNNEL_STATUSES:
            raise ValueError(f"status må være en av: {', '.join(sorted(TUNNEL_STATUSES))}")
        return s


class IpamTunnelUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, max_length=128)
    status: str | None = None
    profile_id: int | None = Field(None, ge=1)
    description: str | None = None

    @field_validator("status")
    @classmethod
    def status_ok(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if s not in TUNNEL_STATUSES:
            raise ValueError(f"status må være en av: {', '.join(sorted(TUNNEL_STATUSES))}")
        return s


class IpamTunnelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vpn_service_id: int
    profile_id: int | None
    name: str
    slug: str
    status: str
    description: str | None
    created_at: dt.datetime


class IpamTunnelEndpointCreate(BaseModel):
    endpoint: Literal["a", "z"]
    device_id: int | None = Field(None, ge=1)
    interface_id: int | None = Field(None, ge=1)
    site_id: int | None = Field(None, ge=1)
    label: str | None = Field(None, max_length=255)


class IpamTunnelEndpointRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tunnel_id: int
    endpoint: str
    device_id: int | None
    interface_id: int | None
    site_id: int | None
    label: str | None
    device_name: str | None = None
    interface_name: str | None = None


class IpamTunnelPeerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    public_key_ref: str | None = Field(None, max_length=255)
    allowed_ips: list[str] | None = None
    endpoint_host: str | None = Field(None, max_length=255)
    endpoint_port: int | None = Field(None, ge=1, le=65535)
    persistent_keepalive: int | None = Field(None, ge=0, le=86400)
    device_id: int | None = Field(None, ge=1)
    interface_id: int | None = Field(None, ge=1)
    notes: str | None = None

    @field_validator("public_key_ref")
    @classmethod
    def key_ref_ok(cls, v: str | None) -> str | None:
        return normalize_secret_ref(v)

    @field_validator("allowed_ips", mode="before")
    @classmethod
    def ips_ok(cls, v: Any) -> list[str] | None:
        if v is None:
            return None
        items = _csv_or_list(v)
        return items or None


class IpamTunnelPeerUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    public_key_ref: str | None = Field(None, max_length=255)
    allowed_ips: list[str] | None = None
    endpoint_host: str | None = Field(None, max_length=255)
    endpoint_port: int | None = Field(None, ge=1, le=65535)
    persistent_keepalive: int | None = Field(None, ge=0, le=86400)
    device_id: int | None = Field(None, ge=1)
    interface_id: int | None = Field(None, ge=1)
    notes: str | None = None

    @field_validator("public_key_ref")
    @classmethod
    def key_ref_ok(cls, v: str | None) -> str | None:
        return normalize_secret_ref(v)

    @field_validator("allowed_ips", mode="before")
    @classmethod
    def ips_ok(cls, v: Any) -> list[str] | None:
        if v is None:
            return None
        items = _csv_or_list(v)
        return items or None


class IpamTunnelPeerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tunnel_id: int
    name: str
    public_key_ref: str | None
    allowed_ips: list[str] | None
    endpoint_host: str | None
    endpoint_port: int | None
    persistent_keepalive: int | None
    device_id: int | None
    interface_id: int | None
    notes: str | None
    created_at: dt.datetime


class Ipv4PrefixSplitHalfIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    cidr: str = Field(..., min_length=1, max_length=32)

    @field_validator("cidr")
    @classmethod
    def cidr_strip(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("cidr kan ikke være tom")
        return s


class Ipv4PrefixSplitRequest(BaseModel):
    """Del et IPv4-prefiks i to undernett som til sammen dekker hele forelderen (ingen hull)."""

    first: Ipv4PrefixSplitHalfIn
    second: Ipv4PrefixSplitHalfIn
    migrate_inventory: bool = Field(
        True,
        description="Flytt IPAM-inventory og DCIM-tildelinger som peker på forelderen, til riktig barn-prefiks",
    )
    acknowledge_network_broadcast: bool = Field(
        False,
        description="Påkrevd når en eksisterende adresse faller på nettverks- eller broadcast-adresse i et av barna",
    )
    dry_run: bool = Field(True, description="True = kun validering og oppsummering, ingen DB-endring")


class Ipv4PrefixSplitConflictRead(BaseModel):
    address: str
    role: Literal["network", "broadcast"]
    message: str
    subnet_cidr: str = Field(..., description="Barn-prefiks der adressen treffer som nettverk/broadcast")


class Ipv4PrefixSplitEqualPlannedRead(BaseModel):
    cidr: str
    suggested_name: str


class Ipv4PrefixSplitEqualRequest(BaseModel):
    """Lik inndeling: `parent` deles i `2^(new_prefix_len - parent_len)` like barn."""

    new_prefix_len: int = Field(..., ge=1, le=32)
    migrate_inventory: bool = True
    acknowledge_network_broadcast: bool = False
    dry_run: bool = True
    names_by_cidr: dict[str, str] | None = Field(
        default=None,
        description="Valgfritt: kanonisk CIDR-streng → visningsnavn; ellers brukes CIDR som navn",
    )


class Ipv4PrefixSplitEqualResponse(BaseModel):
    dry_run: bool
    has_child_prefixes: bool
    parent_cidr: str
    new_prefix_len: int
    subnet_count: int
    partition_ok: bool
    detail: str | None = None
    planned: list[Ipv4PrefixSplitEqualPlannedRead] = Field(default_factory=list)
    ipam_inventory_on_parent: int = 0
    dcim_iface_on_parent: int = 0
    dcim_device_on_parent: int = 0
    conflicts: list[Ipv4PrefixSplitConflictRead] = Field(default_factory=list)
    created_prefixes: list[Ipv4PrefixRead] = Field(default_factory=list)


class Ipv4PrefixAllocate(BaseModel):
    prefixlen: int = Field(..., ge=1, le=32)
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=128)
    role: str = "access"
    status: str = "active"
    description: str | None = None
    vlan_id: int | None = Field(None, ge=1)
    tenant_id: int | None = Field(None, ge=1)
    subnet_services: SubnetServices | dict[str, Any] | None = None

    @field_validator("slug")
    @classmethod
    def slug_strip_alloc(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if not s:
            raise ValueError("slug kan ikke være tom")
        return s

    @field_validator("role")
    @classmethod
    def role_ok_alloc(cls, v: str) -> str:
        return _role_ok(v, PREFIX_ROLES, "role") or "access"

    @field_validator("status")
    @classmethod
    def status_ok_alloc(cls, v: str) -> str:
        return _role_ok(v, PREFIX_STATUSES, "status") or "active"


class Ipv4AvailablePrefixesRead(BaseModel):
    parent_id: int
    cidr: str
    prefixlen: int
    available: list[str]
    truncated: bool = False


class IpRangeRead(BaseModel):
    start: str
    end: str
    count: int


class Ipv4AvailableRangesRead(BaseModel):
    prefix_id: int
    cidr: str
    role: str
    used_count: int
    used_addresses: list[Ipv4AddressRead] = Field(default_factory=list)
    used_ranges: list[IpRangeRead] = Field(default_factory=list)
    free_ranges: list[IpRangeRead] = Field(default_factory=list)
    free_cidrs: list[str] = Field(default_factory=list)


class Ipv4PrefixSplitResponse(BaseModel):
    dry_run: bool
    has_child_prefixes: bool
    partition_ok: bool
    detail: str | None = Field(None, description="Valideringsfeil eller kort status")
    first_cidr: str | None = None
    second_cidr: str | None = None
    ipam_inventory_on_parent: int = 0
    ipam_migrate_left: int = 0
    ipam_migrate_right: int = 0
    dcim_iface_on_parent: int = 0
    dcim_device_on_parent: int = 0
    conflicts: list[Ipv4PrefixSplitConflictRead] = Field(default_factory=list)
    first_prefix: Ipv4PrefixRead | None = None
    second_prefix: Ipv4PrefixRead | None = None


class Ipv6PrefixCreate(Ipv4PrefixCreate):
    cidr: str = Field(..., min_length=1, max_length=64)


class Ipv6PrefixEnsure(Ipv4PrefixEnsure):
    cidr: str = Field(..., min_length=1, max_length=64)


class Ipv6PrefixUpdate(Ipv4PrefixUpdate):
    cidr: str | None = Field(None, min_length=1, max_length=64)


class Ipv6PrefixRead(BaseModel):
    id: int
    site_id: int
    tenant_id: int | None = None
    vlan_id: int | None = None
    vrf_id: int | None = None
    name: str
    slug: str
    role: str = "access"
    status: str = "active"
    cidr: str
    description: str | None = None
    overlap_policy: str = "site-local"
    dual_stack_group_id: int | None = None
    parent_id: int | None = None
    used_count: int = 0
    created: bool | None = None
    subnet_services: dict[str, Any] | None = None
    created_at: dt.datetime
    updated_at: dt.datetime | None = None
    etag: str | None = None


class Ipv6PrefixAllocate(Ipv4PrefixAllocate):
    prefixlen: int = Field(..., ge=1, le=128)


class Ipv6AddressEnsure(BaseModel):
    ipv6_prefix_id: int | None = Field(None, ge=1)
    prefix_cidr: str | None = Field(None, max_length=64)
    site_id: int | None = Field(None, ge=1)
    site_slug: str | None = Field(None, max_length=64)
    address: str = Field(..., min_length=1, max_length=64)
    mode: str | None = None
    status: str | None = None
    note: str | None = None
    role: str | None = None
    hostname: str | None = None
    fqdn: str | None = None
    dns_name: str | None = None
    owner_type: str | None = None
    owner_ref: str | None = None

    @field_validator("mode")
    @classmethod
    def mode_ok_v6(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = v.strip().lower()
        if s not in _ADDRESS_MODES:
            raise ValueError("mode må være reserve eller assign")
        return s

    @field_validator("role")
    @classmethod
    def role_ok_v6(cls, v: str | None) -> str | None:
        return _role_ok(v, _ADDRESS_ROLES, "role")

    @model_validator(mode="after")
    def prefix_ref_present_v6(self) -> Ipv6AddressEnsure:
        if self.ipv6_prefix_id is None and not (self.prefix_cidr or "").strip():
            raise ValueError("ipv6_prefix_id eller prefix_cidr kreves")
        return self


class Ipv6AddressRequest(BaseModel):
    ipv6_prefix_id: int = Field(..., ge=1)
    mode: str = "reserve"
    preferred_address: str | None = None
    role: str | None = None
    note: str | None = None

    @field_validator("mode")
    @classmethod
    def mode_ok_req_v6(cls, v: str) -> str:
        s = v.strip().lower()
        if s not in _ADDRESS_MODES:
            raise ValueError("mode må være reserve eller assign")
        return s


class Ipv6AddressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    site_id: int
    ipv6_prefix_id: int | None
    address: str
    status: str
    role: str = "host"
    hostname: str | None = None
    fqdn: str | None = None
    dns_name: str | None = None
    owner_type: str | None = None
    owner_ref: str | None = None
    note: str | None = None
    device_id: int | None = None
    interface_id: int | None = None
    created: bool | None = None
    created_at: dt.datetime
    updated_at: dt.datetime
    etag: str | None = None


class Ipv6PrefixAddressGridRow(BaseModel):
    address: str
    address_role: str | None = Field(default=None, description="network | host (IPv6 har ikke broadcast)")
    inventory: Ipv6AddressRead | None = None
    scan_ping_responded: bool | None = None
    scan_mac: str | None = None


class Ipv6PrefixAddressGridRead(BaseModel):
    prefix_id: int
    cidr: str
    active_scan: SubnetScanRead | None = None
    rows: list[Ipv6PrefixAddressGridRow]


class Ipv6AvailableRangesRead(BaseModel):
    prefix_id: int
    cidr: str
    role: str
    used_count: int
    used_addresses: list[Ipv6AddressRead] = Field(default_factory=list)
    used_ranges: list[IpRangeRead] = Field(default_factory=list)
    free_ranges: list[IpRangeRead] = Field(default_factory=list)
    free_cidrs: list[str] = Field(default_factory=list)


class Ipv6PrefixSplitHalfIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    cidr: str = Field(..., min_length=1, max_length=64)

    @field_validator("cidr")
    @classmethod
    def cidr_strip_v6(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("cidr kan ikke være tom")
        return s


class Ipv6PrefixSplitRequest(BaseModel):
    first: Ipv6PrefixSplitHalfIn
    second: Ipv6PrefixSplitHalfIn
    migrate_inventory: bool = True
    dry_run: bool = True


class Ipv6PrefixSplitResponse(BaseModel):
    dry_run: bool
    has_child_prefixes: bool
    partition_ok: bool
    detail: str | None = None
    first_cidr: str | None = None
    second_cidr: str | None = None
    ipam_inventory_on_parent: int = 0
    ipam_migrate_left: int = 0
    ipam_migrate_right: int = 0
    first_prefix: Ipv6PrefixRead | None = None
    second_prefix: Ipv6PrefixRead | None = None


class Ipv6PrefixSplitEqualRequest(BaseModel):
    new_prefix_len: int = Field(..., ge=1, le=128)
    migrate_inventory: bool = True
    dry_run: bool = True
    names_by_cidr: dict[str, str] | None = None


class Ipv6PrefixSplitEqualResponse(BaseModel):
    dry_run: bool
    has_child_prefixes: bool
    parent_cidr: str
    new_prefix_len: int
    subnet_count: int
    partition_ok: bool
    detail: str | None = None
    planned: list[Ipv4PrefixSplitEqualPlannedRead] = Field(default_factory=list)
    ipam_inventory_on_parent: int = 0
    created_prefixes: list[Ipv6PrefixRead] = Field(default_factory=list)


class IpamAuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: dt.datetime
    actor_type: str
    actor_id: int | None
    actor_name: str | None
    action: str
    resource_type: str
    resource_id: int | None
    site_id: int | None
    detail: dict[str, Any] | None = None


class IpamDriftAddress(BaseModel):
    address: str
    status: str | None = None
    role: str | None = None
    mac_address: str | None = None


class PrefixDriftRead(BaseModel):
    prefix_id: int
    cidr: str
    scan_id: int | None = None
    scanned_at: dt.datetime | None = None
    aligned: list[str] = Field(default_factory=list)
    seen_unmanaged: list[IpamDriftAddress] = Field(default_factory=list)
    reserved_missing: list[IpamDriftAddress] = Field(default_factory=list)


class SiteDriftRead(BaseModel):
    site_id: int
    prefixes: list[PrefixDriftRead]


class IpamBulkEnsure(BaseModel):
    update: bool = False
    prefixes: list[Ipv4PrefixEnsure] = Field(default_factory=list)
    addresses: list[Ipv4AddressEnsure] = Field(default_factory=list)
    ipv6_prefixes: list[Ipv6PrefixEnsure] = Field(default_factory=list)
    ipv6_addresses: list[Ipv6AddressEnsure] = Field(default_factory=list)


class IpamBulkItemResult(BaseModel):
    kind: str
    key: str
    ok: bool
    created: bool | None = None
    id: int | None = None
    error: dict[str, Any] | None = None


class IpamBulkEnsureRead(BaseModel):
    results: list[IpamBulkItemResult]
    created: int = 0
    unchanged: int = 0
    failed: int = 0


class IpamWebhookCreate(BaseModel):
    url: str = Field(..., min_length=8, max_length=512)
    secret: str | None = Field(None, max_length=255)
    events: list[str] | None = None
    enabled: bool = True


class IpamWebhookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    events: list[str] | None = None
    enabled: bool
    created_at: dt.datetime


class IpamWebhookDeliveryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    webhook_id: int
    event: str
    status: str
    status_code: int | None
    error: str | None
    created_at: dt.datetime
