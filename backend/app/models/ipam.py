"""IPAM (IPv4 først): prefiks er alltid scoped til én DCIM-site.

Samme CIDR (f.eks. 192.168.1.0/24) kan finnes på flere sites — typisk avdelingskontor
med identisk adresseplan. Unikhet er (site_id, vrf_scope, cidr): samme CIDR i ulike VRF
på samme site er tillatt (overlay vs underlay).
"""

from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
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
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
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
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
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
    cidr: Mapped[str] = mapped_column(String(32), nullable=False)
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
    """L3-VRF (rutekontekst) per site — navn unikt innenfor site."""

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


class IpamVlan(Base):
    """802.1Q VLAN per site; valgfritt koblet til VRF for L3-kontekst."""

    __tablename__ = "ipam_vlans"
    __table_args__ = (
        UniqueConstraint("site_id", "vid", name="uq_ipam_vlan_site_vid"),
        UniqueConstraint("site_id", "slug", name="uq_ipam_vlan_site_slug"),
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

    vrf: Mapped["IpamVrf | None"] = relationship(back_populates="vlans")


class IpamCircuit(Base):
    """Samband (fiber, VPN, WireGuard, radiolinje). Tenant er valgfri — intern WG trenger den ikke."""

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
    is_leased: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    provider_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
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
    """Endepunkt A eller Z på samband; kan peke på DCIM-grensesnitt."""

    __tablename__ = "ipam_circuit_terminations"
    __table_args__ = (UniqueConstraint("circuit_id", "endpoint", name="uq_ipam_circuit_term_endpoint"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    circuit_id: Mapped[int] = mapped_column(
        ForeignKey("ipam_circuits.id", ondelete="CASCADE"),
        nullable=False,
    )
    endpoint: Mapped[str] = mapped_column(String(1), nullable=False)
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
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
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
