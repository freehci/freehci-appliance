"""Servicekatalog: mal, versjon, deployment og instans.

Revision ID: 20260526_service_catalog
Revises: 20260525_integration
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260526_service_catalog"
down_revision: Union[str, Sequence[str], None] = "20260525_integration"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "catalog_service_templates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_catalog_service_template_slug"),
    )
    op.create_table(
        "catalog_service_template_versions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("template_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("spec", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["template_id"], ["catalog_service_templates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("template_id", "version", name="uq_catalog_template_version"),
    )
    op.create_table(
        "catalog_service_deployments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("template_version_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("ipv4_prefix_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="planned"),
        sa.Column("plan_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["template_version_id"], ["catalog_service_template_versions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["ipv4_prefix_id"], ["ipam_ipv4_prefixes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "catalog_service_deployment_steps",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("deployment_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["deployment_id"], ["catalog_service_deployments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "catalog_service_instances",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("template_version_id", sa.Integer(), nullable=False),
        sa.Column("deployment_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("ipv4_address_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["template_version_id"], ["catalog_service_template_versions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["deployment_id"], ["catalog_service_deployments.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["ipv4_address_id"], ["ipam_ipv4_addresses.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_catalog_service_instance_slug"),
    )


def downgrade() -> None:
    op.drop_table("catalog_service_instances")
    op.drop_table("catalog_service_deployment_steps")
    op.drop_table("catalog_service_deployments")
    op.drop_table("catalog_service_template_versions")
    op.drop_table("catalog_service_templates")
