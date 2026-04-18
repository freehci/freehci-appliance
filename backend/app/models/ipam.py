"""IPAM (IPv4 først): prefiks er alltid scoped til én DCIM-site.

Samme CIDR (f.eks. 192.168.1.0/24) kan finnes på flere sites — typisk avdelingskontor
med identisk adresseplan. Unikhet er (site_id, cidr), ikke globalt på CIDR alene.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class IpamIpv4Prefix(Base):
    __tablename__ = "ipam_ipv4_prefixes"
    __table_args__ = (UniqueConstraint("site_id", "cidr", name="uq_ipam_ipv4_site_cidr"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Kanonisk IPv4 CIDR-streng, f.eks. 192.168.1.0/24 (normaliseres i tjenestelaget).
    cidr: Mapped[str] = mapped_column(String(32), nullable=False)
    # Valgfritt: gateway, DNS, DHCP m.m. for integrasjoner (strukturert som JSON-objekt).
    subnet_services: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
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

    owner_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
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
