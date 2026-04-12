"""Nettverksskann: maler, jobber, JSON-resultat per vert og oppdagelseskø for DCIM."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class NetworkScanTemplate(Base):
    """Skanningsmal (innebygd ping/SNMP/port eller egendefinert portliste)."""

    __tablename__ = "network_scan_templates"
    __table_args__ = (UniqueConstraint("slug", name="uq_network_scan_template_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # ping | snmp_quick | tcp_ports
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    is_builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    jobs: Mapped[list["NetworkScanJob"]] = relationship(back_populates="template")
    prefix_bindings: Mapped[list["NetworkScanPrefixBinding"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
    )


class NetworkScanPrefixBinding(Base):
    """Hvilke maler som er tilgjengelige for et gitt IPv4-prefiks (subnet)."""

    __tablename__ = "network_scan_prefix_bindings"
    __table_args__ = (
        UniqueConstraint("template_id", "ipv4_prefix_id", name="uq_netscan_bind_template_prefix"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_id: Mapped[int] = mapped_column(
        ForeignKey("network_scan_templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    ipv4_prefix_id: Mapped[int] = mapped_column(
        ForeignKey("ipam_ipv4_prefixes.id", ondelete="CASCADE"),
        nullable=False,
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    template: Mapped["NetworkScanTemplate"] = relationship(back_populates="prefix_bindings")


class NetworkScanJob(Base):
    """Én kjøring av en mal mot et prefiks (evt. begrenset av foreldre-jobb)."""

    __tablename__ = "network_scan_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_id: Mapped[int] = mapped_column(
        ForeignKey("network_scan_templates.id", ondelete="RESTRICT"),
        nullable=False,
    )
    ipv4_prefix_id: Mapped[int] = mapped_column(
        ForeignKey("ipam_ipv4_prefixes.id", ondelete="CASCADE"),
        nullable=False,
    )
    site_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    cidr: Mapped[str] = mapped_column(String(32), nullable=False)
    parent_job_id: Mapped[int | None] = mapped_column(
        ForeignKey("network_scan_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    # pending | running | completed | failed
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    options_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    hosts_scanned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hosts_matched: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    template: Mapped["NetworkScanTemplate"] = relationship(back_populates="jobs")
    host_results: Mapped[list["NetworkScanHostResult"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )
    discoveries: Mapped[list["NetworkScanDiscovery"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )


class NetworkScanHostResult(Base):
    """JSON-resultat per vert; skjema avhenger av malens kind."""

    __tablename__ = "network_scan_host_results"
    __table_args__ = (UniqueConstraint("job_id", "address", name="uq_netscan_host_job_addr"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("network_scan_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    address: Mapped[str] = mapped_column(String(45), nullable=False)
    result_json: Mapped[dict] = mapped_column(JSON, nullable=False)

    job: Mapped["NetworkScanJob"] = relationship(back_populates="host_results")


class NetworkScanDiscovery(Base):
    """Oppdagede enheter: kø for menneskelig godkjenning eller auto_promoted."""

    __tablename__ = "network_scan_discoveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(
        ForeignKey("network_scan_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    site_id: Mapped[int] = mapped_column(
        ForeignKey("dcim_sites.id", ondelete="CASCADE"),
        nullable=False,
    )
    address: Mapped[str] = mapped_column(String(45), nullable=False)
    name_candidates_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    chosen_name_source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    chosen_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # pending | promoted | rejected | auto_promoted
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    dcim_device_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_device_instances.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    job: Mapped["NetworkScanJob"] = relationship(back_populates="discoveries")
