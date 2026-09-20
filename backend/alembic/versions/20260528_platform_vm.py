"""VM-inventar på cluster, uten observert kapasitet.

Revision ID: 20260528_platform_vm
Revises: 20260527_platform_cluster
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260528_platform_vm"
down_revision: Union[str, Sequence[str], None] = "20260527_platform_cluster"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_virtual_machines",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("cluster_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="planned"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["cluster_id"], ["platform_clusters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_platform_vm_slug"),
    )
    with op.batch_alter_table("catalog_service_deployments") as batch:
        batch.add_column(sa.Column("vm_id", sa.Integer(), nullable=True))
        batch.alter_column("device_id", existing_type=sa.Integer(), nullable=True)
        batch.create_foreign_key(
            "fk_catalog_deployment_vm",
            "platform_virtual_machines",
            ["vm_id"],
            ["id"],
            ondelete="SET NULL",
        )
    with op.batch_alter_table("catalog_service_instances") as batch:
        batch.add_column(sa.Column("vm_id", sa.Integer(), nullable=True))
        batch.alter_column("device_id", existing_type=sa.Integer(), nullable=True)
        batch.create_foreign_key(
            "fk_catalog_instance_vm",
            "platform_virtual_machines",
            ["vm_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("catalog_service_instances") as batch:
        batch.drop_constraint("fk_catalog_instance_vm", type_="foreignkey")
        batch.drop_column("vm_id")
        batch.alter_column("device_id", existing_type=sa.Integer(), nullable=False)
    with op.batch_alter_table("catalog_service_deployments") as batch:
        batch.drop_constraint("fk_catalog_deployment_vm", type_="foreignkey")
        batch.drop_column("vm_id")
        batch.alter_column("device_id", existing_type=sa.Integer(), nullable=False)
    op.drop_table("platform_virtual_machines")
