"""Device types, model/instance links, flexible attributes on instances.

Revision ID: 20260414_device_types
Revises: 20260413_dm_images
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260414_device_types"
down_revision: Union[str, Sequence[str], None] = "20260413_dm_images"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_device_types",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
        sa.UniqueConstraint("name"),
    )

    op.add_column(
        "dcim_device_models",
        sa.Column("device_type_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_dcim_device_models_device_type",
        "dcim_device_models",
        "dcim_device_types",
        ["device_type_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column(
        "dcim_device_instances",
        sa.Column("device_type_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_dcim_device_instances_device_type",
        "dcim_device_instances",
        "dcim_device_types",
        ["device_type_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.add_column(
        "dcim_device_instances",
        sa.Column("attributes", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("dcim_device_instances", "attributes")
    op.drop_constraint("fk_dcim_device_instances_device_type", "dcim_device_instances", type_="foreignkey")
    op.drop_column("dcim_device_instances", "device_type_id")
    op.drop_constraint("fk_dcim_device_models_device_type", "dcim_device_models", type_="foreignkey")
    op.drop_column("dcim_device_models", "device_type_id")
    op.drop_table("dcim_device_types")
