"""Registrert firmware/BIOS/OS-image uten påføring.

Revision ID: 20260604_dcim_artifact
Revises: 20260603_vif_ipv4
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260604_dcim_artifact"
down_revision: Union[str, Sequence[str], None] = "20260603_vif_ipv4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_device_artifacts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False, server_default="other"),
        sa.Column("version", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_dcim_device_artifact_slug"),
    )
    op.create_table(
        "dcim_device_artifact_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("artifact_id", sa.Integer(), nullable=False),
        sa.Column("intent", sa.String(length=32), nullable=False, server_default="recorded"),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["artifact_id"], ["dcim_device_artifacts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", "artifact_id", name="uq_dcim_device_artifact_record"),
    )
    with op.batch_alter_table("catalog_service_deployments") as batch:
        batch.add_column(sa.Column("artifact_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_catalog_deploy_artifact",
            "dcim_device_artifacts",
            ["artifact_id"],
            ["id"],
            ondelete="SET NULL",
        )
    with op.batch_alter_table("catalog_service_instances") as batch:
        batch.add_column(sa.Column("artifact_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_catalog_instance_artifact",
            "dcim_device_artifacts",
            ["artifact_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("catalog_service_instances") as batch:
        batch.drop_constraint("fk_catalog_instance_artifact", type_="foreignkey")
        batch.drop_column("artifact_id")
    with op.batch_alter_table("catalog_service_deployments") as batch:
        batch.drop_constraint("fk_catalog_deploy_artifact", type_="foreignkey")
        batch.drop_column("artifact_id")
    op.drop_table("dcim_device_artifact_records")
    op.drop_table("dcim_device_artifacts")
