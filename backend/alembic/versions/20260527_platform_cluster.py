"""Cluster-inventar og katalogkobling.

Revision ID: 20260527_platform_cluster
Revises: 20260526_service_catalog
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260527_platform_cluster"
down_revision: Union[str, Sequence[str], None] = "20260526_service_catalog"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_clusters",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False, server_default="other"),
        sa.Column("site_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_platform_cluster_slug"),
    )
    op.create_table(
        "platform_cluster_members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("cluster_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="node"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["cluster_id"], ["platform_clusters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cluster_id", "device_id", name="uq_platform_cluster_member"),
    )
    with op.batch_alter_table("catalog_service_deployments") as batch:
        batch.add_column(sa.Column("cluster_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_catalog_deployment_cluster",
            "platform_clusters",
            ["cluster_id"],
            ["id"],
            ondelete="SET NULL",
        )
    with op.batch_alter_table("catalog_service_instances") as batch:
        batch.add_column(sa.Column("cluster_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_catalog_instance_cluster",
            "platform_clusters",
            ["cluster_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    op.drop_constraint("fk_catalog_instance_cluster", "catalog_service_instances", type_="foreignkey")
    op.drop_column("catalog_service_instances", "cluster_id")
    op.drop_constraint("fk_catalog_deployment_cluster", "catalog_service_deployments", type_="foreignkey")
    op.drop_column("catalog_service_deployments", "cluster_id")
    op.drop_table("platform_cluster_members")
    op.drop_table("platform_clusters")
