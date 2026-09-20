"""Versjonert servicekatalog og én vertikal deploymentflyt mot Device."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ServiceTemplate(Base):
    __tablename__ = "catalog_service_templates"
    __table_args__ = (UniqueConstraint("slug", name="uq_catalog_service_template_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    versions: Mapped[list["ServiceTemplateVersion"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="ServiceTemplateVersion.id",
    )


class ServiceTemplateVersion(Base):
    __tablename__ = "catalog_service_template_versions"
    __table_args__ = (UniqueConstraint("template_id", "version", name="uq_catalog_template_version"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_id: Mapped[int] = mapped_column(
        ForeignKey("catalog_service_templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    spec: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    template: Mapped["ServiceTemplate"] = relationship(back_populates="versions")


class ServiceDeployment(Base):
    __tablename__ = "catalog_service_deployments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_version_id: Mapped[int] = mapped_column(
        ForeignKey("catalog_service_template_versions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    device_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_device_instances.id", ondelete="RESTRICT"),
        nullable=True,
    )
    ipv4_prefix_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_ipv4_prefixes.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    plan_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cluster_id: Mapped[int | None] = mapped_column(
        ForeignKey("platform_clusters.id", ondelete="SET NULL"),
        nullable=True,
    )
    vm_id: Mapped[int | None] = mapped_column(
        ForeignKey("platform_virtual_machines.id", ondelete="SET NULL"),
        nullable=True,
    )
    storage_pool_id: Mapped[int | None] = mapped_column(
        ForeignKey("platform_storage_pools.id", ondelete="SET NULL"),
        nullable=True,
    )

    steps: Mapped[list["ServiceDeploymentStep"]] = relationship(
        back_populates="deployment",
        cascade="all, delete-orphan",
        order_by="ServiceDeploymentStep.id",
    )


class ServiceDeploymentStep(Base):
    __tablename__ = "catalog_service_deployment_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deployment_id: Mapped[int] = mapped_column(
        ForeignKey("catalog_service_deployments.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    deployment: Mapped["ServiceDeployment"] = relationship(back_populates="steps")


class ServiceInstance(Base):
    __tablename__ = "catalog_service_instances"
    __table_args__ = (UniqueConstraint("slug", name="uq_catalog_service_instance_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    template_version_id: Mapped[int] = mapped_column(
        ForeignKey("catalog_service_template_versions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    deployment_id: Mapped[int] = mapped_column(
        ForeignKey("catalog_service_deployments.id", ondelete="RESTRICT"),
        nullable=False,
    )
    device_id: Mapped[int | None] = mapped_column(
        ForeignKey("dcim_device_instances.id", ondelete="RESTRICT"),
        nullable=True,
    )
    ipv4_address_id: Mapped[int | None] = mapped_column(
        ForeignKey("ipam_ipv4_addresses.id", ondelete="SET NULL"),
        nullable=True,
    )
    cluster_id: Mapped[int | None] = mapped_column(
        ForeignKey("platform_clusters.id", ondelete="SET NULL"),
        nullable=True,
    )
    vm_id: Mapped[int | None] = mapped_column(
        ForeignKey("platform_virtual_machines.id", ondelete="SET NULL"),
        nullable=True,
    )
    storage_pool_id: Mapped[int | None] = mapped_column(
        ForeignKey("platform_storage_pools.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
