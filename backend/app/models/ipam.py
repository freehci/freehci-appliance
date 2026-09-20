"""IPAM (IPv4 først): prefiks er alltid scoped til én DCIM-site.

Samme CIDR (f.eks. 192.168.1.0/24) kan finnes på flere sites — typisk avdelingskontor
med identisk adresseplan. Unikhet er (site_id, vrf_scope, cidr): samme CIDR i ulike VRF
på samme site er tillatt (overlay vs underlay).
"""

from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.tenant import Tenant


class IpamIpv4Prefix(Base):
    __tablename__ = "ipam_ipv4_prefixes"
    __table_args__ = (
        UniqueConstraint("site_id", "vrf_scope", "cidr", name="uq_ipam_ipv4_site_vrf_cidr"),
        UniqueConstraint("site_id", "slug", name="uq_ipam_ipv4_site_slug"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    tenant_id: Mapped[int | None] = mapped_column(
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
    )
    vlan_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_vlans.id", ondelete="SET NULL"),
        nullable=True,
    )
    vrf_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_vrfs.id", ondelete="SET NULL"),
        nullable=True,
    )
    # 0 når vrf_id er NULL — gjør unikhet (site, vrf, cidr) deterministisk i SQLite/Postgres.
    vrf_scope: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    # Formål (container, access, overlay-*, …) — ikke livsløp. Se status.
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="access")
    # Livsløp: planned | active | reserved | deprecated.
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    overlap_policy: Mapped[str] = mapped_column(String(16), nullable=False, default="site-local")
    dual_stack_group_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Kanonisk IPv4 CIDR-streng, f.eks. 192.168.1.0/24 (normaliseres i tjenestelaget).
    cidr: Mapped[str] = mapped_column(String(32), nullable=False)
    # Typet JSON: gateway, dns[], ntp[], dhcp_server, dhcp_range, domain, mtu.
    subnet_services: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    # Python-default er påkrevd: Alembic 20260511 la til kolonnen uten server_default.
    # INSERT uten verdi ble NOT NULL → IntegrityError, maskert som prefix_conflict.
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class IpamSubnetScan(Base):
    """Én kjøring av subnett-skann (ping først; SNMP/port kan komme senere)."""

    __tablename__ = "ipam_subnet_scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    ipv4_prefix_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_ipv4_prefixes.id", ondelete="SET NULL"),
        nullable=True,
    )
    ipv6_prefix_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_ipv6_prefixes.id", ondelete="SET NULL"),
        nullable=True,
    )
    cidr: Mapped[str] = mapped_column(String(64), nullable=False)
    method: Mapped[str] = mapped_column(String(32), nullable=False, default="ping")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    hosts_scanned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hosts_responding: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    hosts: Mapped[list["IpamScanHost"]] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
    )


class IpamScanHost(Base):
    """Vert funnet ved skann (ping-svar; MAC fra lokal ARP/neighbor der OS gir det)."""

    __tablename__ = "ipam_scan_hosts"
    __table_args__ = (UniqueConstraint("scan_id", "address", name="uq_ipam_scan_host_scan_addr"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scan_id: Mapped[int] = mapped_column(
        ForeignKey("ipam_subnet_scans.id", ondelete="CASCADE"),
        nullable=False,
    )
    address: Mapped[str] = mapped_column(String(45), nullable=False)
    mac_address: Mapped[str | None] = mapped_column(String(32), nullable=True)
    ping_responded: Mapped[bool] = mapped_column(default=True, nullable=False)

    scan: Mapped["IpamSubnetScan"] = relationship(back_populates="hosts")


class IpamIpv4Address(Base):
    """Varig inventory av IPv4-adresser per site (oppdaget/reservert/tildelt)."""

    __tablename__ = "ipam_ipv4_addresses"
    __table_args__ = (UniqueConstraint("site_id", "address", name="uq_ipam_ipv4_addr_site_address"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    ipv4_prefix_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_ipv4_prefixes.id", ondelete="SET NULL"),
        nullable=True,
    )
    address: Mapped[str] = mapped_column(String(45), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="discovered")
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="host")
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fqdn: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dns_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    owner_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    owner_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    owner_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    mac_address: Mapped[str | None] = mapped_column(String(32), nullable=True)
    last_seen_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    device_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_device_types.id", ondelete="SET NULL"),
        nullable=True,
    )
    device_model_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_device_models.id", ondelete="SET NULL"),
        nullable=True,
    )
    device_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_device_instances.id", ondelete="SET NULL"),
        nullable=True,
    )
    interface_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_device_interfaces.id", ondelete="SET NULL"),
        nullable=True,
    )
    interface_ip_assignment_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_interface_ip_assignments.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class IpamVrf(Base):
    """Logisk L3-VRF (rutekontekst) per site — ikke enhetsinstans.

    Instans (PE/VRF på boks) kommer senere. RD valideres som ASN:nn eller IPv4:nn.
    """

    __tablename__ = "ipam_vrfs"
    __table_args__ = (
        UniqueConstraint("site_id", "name", name="uq_ipam_vrf_site_name"),
        UniqueConstraint("site_id", "slug", name="uq_ipam_vrf_site_slug"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    route_distinguisher: Mapped[str | None] = mapped_column(String(64), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    vlans: Mapped[list["IpamVlan"]] = relationship(back_populates="vrf")


class IpamVlanGroup(Base):
    """VID-namespace. Samme 802.1Q-ID kan finnes i ulike grupper på samme site."""

    __tablename__ = "ipam_vlan_groups"
    __table_args__ = (
        UniqueConstraint("site_id", "slug", name="uq_ipam_vlan_group_site_slug"),
        UniqueConstraint("site_id", "name", name="uq_ipam_vlan_group_site_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    vlans: Mapped[list["IpamVlan"]] = relationship(back_populates="vlan_group")


class IpamVlan(Base):
    """802.1Q VLAN; VID unikt i VLAN-gruppen, valgfritt koblet til logisk VRF."""

    __tablename__ = "ipam_vlans"
    __table_args__ = (
        UniqueConstraint("vlan_group_id", "vid", name="uq_ipam_vlan_group_vid"),
        UniqueConstraint("site_id", "slug", name="uq_ipam_vlan_site_slug"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    vlan_group_id: Mapped[int] = mapped_column(
        ForeignKey("ipam_vlan_groups.id", ondelete="RESTRICT"),
        nullable=False,
    )
    tenant_id: Mapped[int | None] = mapped_column(
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
    )
    vid: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    vrf_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_vrfs.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    vlan_group: Mapped["IpamVlanGroup"] = relationship(back_populates="vlans")
    vrf: Mapped["IpamVrf | None"] = relationship(back_populates="vlans")


class IpamProvider(Base):
    """Global leverandør/operatør. Opprettes eksplisitt — aldri gjettet fra fritekst."""

    __tablename__ = "ipam_providers"
    __table_args__ = (UniqueConstraint("slug", name="uq_ipam_provider_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    asn: Mapped[int | None] = mapped_column(Integer, nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    accounts: Mapped[list["IpamProviderAccount"]] = relationship(
        back_populates="provider",
        cascade="all, delete-orphan",
    )


class IpamProviderAccount(Base):
    """Kundekonto hos en leverandør, valgfritt per tenant."""

    __tablename__ = "ipam_provider_accounts"
    __table_args__ = (UniqueConstraint("provider_id", "slug", name="uq_ipam_provider_account_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider_id: Mapped[int] = mapped_column(
        ForeignKey("ipam_providers.id", ondelete="CASCADE"),
        nullable=False,
    )
    tenant_id: Mapped[int | None] = mapped_column(
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    account_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    provider: Mapped["IpamProvider"] = relationship(back_populates="accounts")


class IpamCircuit(Base):
    """Transport mellom to punkter. Overlay (VPN) er VPNService etter manuell klassifisering.

    `layer` er nullable og fylles aldri automatisk fra `circuit_type`.
    `provider_name` er historisk fritekst; `provider_id` settes bare når brukeren velger.
    """

    __tablename__ = "ipam_circuits"
    __table_args__ = (UniqueConstraint("tenant_scope", "circuit_number", name="uq_ipam_circuit_tenant_scope_number"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int | None] = mapped_column(
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
    )
    tenant_scope: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    a_site_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_sites.id", ondelete="SET NULL"),
        nullable=True,
    )
    z_site_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_sites.id", ondelete="SET NULL"),
        nullable=True,
    )
    circuit_number: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    circuit_type: Mapped[str] = mapped_column(String(32), nullable=False)
    layer: Mapped[str | None] = mapped_column(String(16), nullable=True)
    is_leased: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    provider_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_providers.id", ondelete="SET NULL"),
        nullable=True,
    )
    provider_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_provider_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    established_on: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    contract_end_on: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    tenant: Mapped["Tenant | None"] = relationship("Tenant", back_populates="circuits")
    terminations: Mapped[list["IpamCircuitTermination"]] = relationship(
        back_populates="circuit",
        cascade="all, delete-orphan",
    )


class IpamCircuitTermination(Base):
    """Endepunkt A eller Z på samband; peker på Device og/eller Interface."""

    __tablename__ = "ipam_circuit_terminations"
    __table_args__ = (UniqueConstraint("circuit_id", "endpoint", name="uq_ipam_circuit_term_endpoint"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    circuit_id: Mapped[int] = mapped_column(
        ForeignKey("ipam_circuits.id", ondelete="CASCADE"),
        nullable=False,
    )
    endpoint: Mapped[str] = mapped_column(String(1), nullable=False)
    device_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("dcim_device_instances.id", ondelete="SET NULL"),
        nullable=True,
    )
    interface_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("dcim_device_interfaces.id", ondelete="SET NULL"),
        nullable=True,
    )
    site_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_sites.id", ondelete="SET NULL"),
        nullable=True,
    )
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)

    circuit: Mapped["IpamCircuit"] = relationship(back_populates="terminations")


class IpamVpnService(Base):
    """Overlay-identitet (VPN). Kan peke bakover til et klassifisert samband."""

    __tablename__ = "ipam_vpn_services"
    __table_args__ = (UniqueConstraint("tenant_scope", "slug", name="uq_ipam_vpn_service_scope_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int | None] = mapped_column(
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
    )
    tenant_scope: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    vpn_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_circuit_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_circuits.id", ondelete="SET NULL"),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    tunnels: Mapped[list["IpamTunnel"]] = relationship(
        back_populates="vpn_service",
        cascade="all, delete-orphan",
    )


class IpamTunnelProfile(Base):
    """Gjenbrukbar tunnelprofil (MTU, listen-port). Ingen nøkkelmateriale."""

    __tablename__ = "ipam_tunnel_profiles"
    __table_args__ = (UniqueConstraint("slug", name="uq_ipam_tunnel_profile_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    vpn_type: Mapped[str] = mapped_column(String(32), nullable=False)
    settings: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class IpamTunnel(Base):
    """Én tunnel under en VPN-tjeneste."""

    __tablename__ = "ipam_tunnels"
    __table_args__ = (UniqueConstraint("vpn_service_id", "slug", name="uq_ipam_tunnel_vpn_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vpn_service_id: Mapped[int] = mapped_column(
        ForeignKey("ipam_vpn_services.id", ondelete="CASCADE"),
        nullable=False,
    )
    profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_tunnel_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    vpn_service: Mapped["IpamVpnService"] = relationship(back_populates="tunnels")
    endpoints: Mapped[list["IpamTunnelEndpoint"]] = relationship(
        back_populates="tunnel",
        cascade="all, delete-orphan",
    )
    peers: Mapped[list["IpamTunnelPeer"]] = relationship(
        back_populates="tunnel",
        cascade="all, delete-orphan",
    )


class IpamTunnelEndpoint(Base):
    """A/Z-ende på en tunnel (Device/Interface)."""

    __tablename__ = "ipam_tunnel_endpoints"
    __table_args__ = (UniqueConstraint("tunnel_id", "endpoint", name="uq_ipam_tunnel_endpoint"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tunnel_id: Mapped[int] = mapped_column(
        ForeignKey("ipam_tunnels.id", ondelete="CASCADE"),
        nullable=False,
    )
    endpoint: Mapped[str] = mapped_column(String(1), nullable=False)
    device_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("dcim_device_instances.id", ondelete="SET NULL"),
        nullable=True,
    )
    interface_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("dcim_device_interfaces.id", ondelete="SET NULL"),
        nullable=True,
    )
    site_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_sites.id", ondelete="SET NULL"),
        nullable=True,
    )
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)

    tunnel: Mapped["IpamTunnel"] = relationship(back_populates="endpoints")


class IpamTunnelPeer(Base):
    """Peer på en tunnel. Nøkler er referanser (`secret:…`), aldri nøkkelmateriale."""

    __tablename__ = "ipam_tunnel_peers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tunnel_id: Mapped[int] = mapped_column(
        ForeignKey("ipam_tunnels.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    public_key_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    allowed_ips: Mapped[list | None] = mapped_column(JSON, nullable=True)
    endpoint_host: Mapped[str | None] = mapped_column(String(255), nullable=True)
    endpoint_port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    persistent_keepalive: Mapped[int | None] = mapped_column(Integer, nullable=True)
    device_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("dcim_device_instances.id", ondelete="SET NULL"),
        nullable=True,
    )
    interface_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("dcim_device_interfaces.id", ondelete="SET NULL"),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    tunnel: Mapped["IpamTunnel"] = relationship(back_populates="peers")


class IpamIdempotencyKey(Base):
    """Idempotency-Key for request/allocate — én nøkkel, ett resultat."""

    __tablename__ = "ipam_idempotency_keys"
    __table_args__ = (UniqueConstraint("key", name="uq_ipam_idempotency_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    scope: Mapped[str] = mapped_column(String(64), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    response_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class IpamIpv6Prefix(Base):
    __tablename__ = "ipam_ipv6_prefixes"
    __table_args__ = (
        UniqueConstraint("site_id", "vrf_scope", "cidr", name="uq_ipam_ipv6_site_vrf_cidr"),
        UniqueConstraint("site_id", "slug", name="uq_ipam_ipv6_site_slug"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("dcim_sites.id", ondelete="CASCADE"), nullable=False)
    tenant_id: Mapped[int | None] = mapped_column(ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True)
    vlan_id: Mapped[int | None] = mapped_column(ForeignKey("ipam_vlans.id", ondelete="SET NULL"), nullable=True)
    vrf_id: Mapped[int | None] = mapped_column(ForeignKey("ipam_vrfs.id", ondelete="SET NULL"), nullable=True)
    vrf_scope: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="access")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    overlap_policy: Mapped[str] = mapped_column(String(16), nullable=False, default="site-local")
    dual_stack_group_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cidr: Mapped[str] = mapped_column(String(64), nullable=False)
    subnet_services: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class IpamIpv6Address(Base):
    __tablename__ = "ipam_ipv6_addresses"
    __table_args__ = (UniqueConstraint("site_id", "address", name="uq_ipam_ipv6_addr_site_address"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("dcim_sites.id", ondelete="CASCADE"), nullable=False)
    ipv6_prefix_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_ipv6_prefixes.id", ondelete="SET NULL"),
        nullable=True,
    )
    address: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="discovered")
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="host")
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fqdn: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dns_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    owner_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    owner_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    mac_address: Mapped[str | None] = mapped_column(String(32), nullable=True)
    last_seen_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    device_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_device_instances.id", ondelete="SET NULL"),
        nullable=True,
    )
    interface_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_device_interfaces.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class IpamAuditEvent(Base):
    __tablename__ = "ipam_audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    actor_type: Mapped[str] = mapped_column(String(32), nullable=False, default="system")
    actor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(32), nullable=False)
    resource_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    site_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class IpamWebhook(Base):
    __tablename__ = "ipam_webhooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    events: Mapped[list | None] = mapped_column(JSON, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class IpamWebhookDelivery(Base):
    __tablename__ = "ipam_webhook_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    webhook_id: Mapped[int] = mapped_column(ForeignKey("ipam_webhooks.id", ondelete="CASCADE"), nullable=False)
    event: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class IpamAutonomousSystem(Base):
    """32-bit AS. Offentlig ASN er globalt unik; privat ASN er unik per tenant_scope."""

    __tablename__ = "ipam_autonomous_systems"
    __table_args__ = (UniqueConstraint("tenant_scope", "asn", name="uq_ipam_as_scope_asn"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asn: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tenant_id: Mapped[int | None] = mapped_column(
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
    )
    tenant_scope: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    assignments: Mapped[list["IpamAsAssignment"]] = relationship(
        back_populates="autonomous_system",
        cascade="all, delete-orphan",
    )


class IpamAsAssignment(Base):
    """Ett AS på flere sites; én site kan ha flere AS. Unikt per (AS, site, VRF)."""

    __tablename__ = "ipam_as_assignments"
    __table_args__ = (
        UniqueConstraint("autonomous_system_id", "site_id", "vrf_scope", name="uq_ipam_as_assign_site_vrf"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    autonomous_system_id: Mapped[int] = mapped_column(
        ForeignKey("ipam_autonomous_systems.id", ondelete="CASCADE"),
        nullable=False,
    )
    site_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    vrf_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_vrfs.id", ondelete="SET NULL"),
        nullable=True,
    )
    vrf_scope: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    autonomous_system: Mapped["IpamAutonomousSystem"] = relationship(back_populates="assignments")


class IpamBgpSession(Base):
    """Én BGP-sesjon mot én peer-IP. IPv4 og IPv6 er address families, ikke to sesjoner."""

    __tablename__ = "ipam_bgp_sessions"
    __table_args__ = (
        UniqueConstraint("site_id", "local_as_id", "peer_ip", "vrf_scope", name="uq_ipam_bgp_peer"),
        UniqueConstraint("site_id", "slug", name="uq_ipam_bgp_site_slug"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    local_as_id: Mapped[int] = mapped_column(
        ForeignKey("ipam_autonomous_systems.id", ondelete="RESTRICT"),
        nullable=False,
    )
    remote_as_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_autonomous_systems.id", ondelete="SET NULL"),
        nullable=True,
    )
    remote_asn: Mapped[int] = mapped_column(BigInteger, nullable=False)
    peer_ip: Mapped[str] = mapped_column(String(64), nullable=False)
    vrf_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_vrfs.id", ondelete="SET NULL"),
        nullable=True,
    )
    vrf_scope: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    address_families: Mapped[list | None] = mapped_column(JSON, nullable=True)
    desired_status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    observed_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    local_device_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("dcim_device_instances.id", ondelete="SET NULL"),
        nullable=True,
    )
    local_interface_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("dcim_device_interfaces.id", ondelete="SET NULL"),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
