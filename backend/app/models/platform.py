"""Cluster-inventar. VM/lagring kommer når en flyt trenger dem."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PlatformCluster(Base):
    __tablename__ = "platform_clusters"
    __table_args__ = (UniqueConstraint("slug", name="uq_platform_cluster_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False, default="other")
    site_id: Mapped[int | None] = mapped_column(ForeignKey("dcim_sites.id", ondelete="SET NULL"), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    members: Mapped[list["PlatformClusterMember"]] = relationship(
        back_populates="cluster",
        cascade="all, delete-orphan",
        order_by="PlatformClusterMember.id",
    )
    vms: Mapped[list["PlatformVirtualMachine"]] = relationship(
        back_populates="cluster",
        cascade="all, delete-orphan",
        order_by="PlatformVirtualMachine.id",
    )
    storage_pools: Mapped[list["PlatformStoragePool"]] = relationship(
        back_populates="cluster",
        cascade="all, delete-orphan",
        order_by="PlatformStoragePool.id",
    )


class PlatformClusterMember(Base):
    __tablename__ = "platform_cluster_members"
    __table_args__ = (UniqueConstraint("cluster_id", "device_id", name="uq_platform_cluster_member"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("platform_clusters.id", ondelete="CASCADE"), nullable=False)
    device_id: Mapped[int] = mapped_column(ForeignKey("dcim_device_instances.id", ondelete="RESTRICT"), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="node")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cluster: Mapped["PlatformCluster"] = relationship(back_populates="members")


class PlatformVirtualMachine(Base):
    """Registrert VM-inventar. Ingen observert strømtilstand eller oppfunnet kapasitet."""

    __tablename__ = "platform_virtual_machines"
    __table_args__ = (UniqueConstraint("slug", name="uq_platform_vm_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("platform_clusters.id", ondelete="CASCADE"), nullable=False)
    device_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_device_instances.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cluster: Mapped["PlatformCluster"] = relationship(back_populates="vms")
    interfaces: Mapped[list["PlatformVirtualInterface"]] = relationship(
        back_populates="vm",
        cascade="all, delete-orphan",
        order_by="PlatformVirtualInterface.id",
    )
    disks: Mapped[list["PlatformVirtualDisk"]] = relationship(
        back_populates="vm",
        cascade="all, delete-orphan",
        order_by="PlatformVirtualDisk.id",
    )


class PlatformStoragePool(Base):
    """Registrert lagringspool. Ingen oppfunnet kapasitet eller IOPS."""

    __tablename__ = "platform_storage_pools"
    __table_args__ = (UniqueConstraint("slug", name="uq_platform_storage_pool_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("platform_clusters.id", ondelete="CASCADE"), nullable=False)
    kind: Mapped[str] = mapped_column(String(32), nullable=False, default="other")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cluster: Mapped["PlatformCluster"] = relationship(back_populates="storage_pools")
    disks: Mapped[list["PlatformVirtualDisk"]] = relationship(back_populates="storage_pool")


class PlatformVirtualInterface(Base):
    """Registrert virtuelt grensesnitt. Ingen oppfunnet MAC eller observert lenketilstand."""

    __tablename__ = "platform_virtual_interfaces"
    __table_args__ = (UniqueConstraint("slug", name="uq_platform_vif_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    vm_id: Mapped[int] = mapped_column(ForeignKey("platform_virtual_machines.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    vm: Mapped["PlatformVirtualMachine"] = relationship(back_populates="interfaces")


class PlatformVirtualDisk(Base):
    """Registrert disk eller volum. Ingen oppfunnet kapasitet eller IOPS."""

    __tablename__ = "platform_virtual_disks"
    __table_args__ = (UniqueConstraint("slug", name="uq_platform_vdisk_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    vm_id: Mapped[int] = mapped_column(ForeignKey("platform_virtual_machines.id", ondelete="CASCADE"), nullable=False)
    storage_pool_id: Mapped[int | None] = mapped_column(
        ForeignKey("platform_storage_pools.id", ondelete="SET NULL"),
        nullable=True,
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False, default="other")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    vm: Mapped["PlatformVirtualMachine"] = relationship(back_populates="disks")
    storage_pool: Mapped["PlatformStoragePool | None"] = relationship(back_populates="disks")
