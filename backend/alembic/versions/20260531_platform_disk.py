"""Disk eller volum på VM uten kapasitetstall.

Revision ID: 20260531_platform_disk
Revises: 20260530_platform_vif
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260531_platform_disk"
down_revision: Union[str, Sequence[str], None] = "20260530_platform_vif"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_virtual_disks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("vm_id", sa.Integer(), nullable=False),
        sa.Column("storage_pool_id", sa.Integer(), nullable=True),
        sa.Column("kind", sa.String(length=32), nullable=False, server_default="other"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="planned"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["vm_id"], ["platform_virtual_machines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["storage_pool_id"], ["platform_storage_pools.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_platform_vdisk_slug"),
    )
    with op.batch_alter_table("catalog_service_deployments") as batch:
        batch.add_column(sa.Column("virtual_disk_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_catalog_deployment_disk",
            "platform_virtual_disks",
            ["virtual_disk_id"],
            ["id"],
            ondelete="SET NULL",
        )
    with op.batch_alter_table("catalog_service_instances") as batch:
        batch.add_column(sa.Column("virtual_disk_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_catalog_instance_disk",
            "platform_virtual_disks",
            ["virtual_disk_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("catalog_service_instances") as batch:
        batch.drop_constraint("fk_catalog_instance_disk", type_="foreignkey")
        batch.drop_column("virtual_disk_id")
    with op.batch_alter_table("catalog_service_deployments") as batch:
        batch.drop_constraint("fk_catalog_deployment_disk", type_="foreignkey")
        batch.drop_column("virtual_disk_id")
    op.drop_table("platform_virtual_disks")
