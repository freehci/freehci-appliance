"""Lagringspool på cluster uten kapasitetstall.

Revision ID: 20260529_platform_storage
Revises: 20260528_platform_vm
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260529_platform_storage"
down_revision: Union[str, Sequence[str], None] = "20260528_platform_vm"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_storage_pools",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("cluster_id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False, server_default="other"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="planned"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["cluster_id"], ["platform_clusters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_platform_storage_pool_slug"),
    )
    with op.batch_alter_table("catalog_service_deployments") as batch:
        batch.add_column(sa.Column("storage_pool_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_catalog_deployment_storage",
            "platform_storage_pools",
            ["storage_pool_id"],
            ["id"],
            ondelete="SET NULL",
        )
    with op.batch_alter_table("catalog_service_instances") as batch:
        batch.add_column(sa.Column("storage_pool_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_catalog_instance_storage",
            "platform_storage_pools",
            ["storage_pool_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("catalog_service_instances") as batch:
        batch.drop_constraint("fk_catalog_instance_storage", type_="foreignkey")
        batch.drop_column("storage_pool_id")
    with op.batch_alter_table("catalog_service_deployments") as batch:
        batch.drop_constraint("fk_catalog_deployment_storage", type_="foreignkey")
        batch.drop_column("storage_pool_id")
    op.drop_table("platform_storage_pools")
