"""Virtuelt grensesnitt på VM uten oppfunnet MAC.

Revision ID: 20260530_platform_vif
Revises: 20260529_platform_storage
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260530_platform_vif"
down_revision: Union[str, Sequence[str], None] = "20260529_platform_storage"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_virtual_interfaces",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("vm_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="planned"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["vm_id"], ["platform_virtual_machines.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_platform_vif_slug"),
    )
    with op.batch_alter_table("catalog_service_deployments") as batch:
        batch.add_column(sa.Column("virtual_interface_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_catalog_deployment_vif",
            "platform_virtual_interfaces",
            ["virtual_interface_id"],
            ["id"],
            ondelete="SET NULL",
        )
    with op.batch_alter_table("catalog_service_instances") as batch:
        batch.add_column(sa.Column("virtual_interface_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_catalog_instance_vif",
            "platform_virtual_interfaces",
            ["virtual_interface_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("catalog_service_instances") as batch:
        batch.drop_constraint("fk_catalog_instance_vif", type_="foreignkey")
        batch.drop_column("virtual_interface_id")
    with op.batch_alter_table("catalog_service_deployments") as batch:
        batch.drop_constraint("fk_catalog_deployment_vif", type_="foreignkey")
        batch.drop_column("virtual_interface_id")
    op.drop_table("platform_virtual_interfaces")
