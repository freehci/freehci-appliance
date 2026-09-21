"""DeviceRole som funksjon, atskilt fra fysisk type.

Revision ID: 20260602_dcim_device_role
Revises: 20260601_platform_cloud
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260602_dcim_device_role"
down_revision: Union[str, Sequence[str], None] = "20260601_platform_cloud"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_device_roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False, server_default="other"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_dcim_device_role_slug"),
        sa.UniqueConstraint("name", name="uq_dcim_device_role_name"),
    )
    with op.batch_alter_table("dcim_device_instances") as batch:
        batch.add_column(sa.Column("device_role_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_dcim_device_role",
            "dcim_device_roles",
            ["device_role_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("dcim_device_instances") as batch:
        batch.drop_constraint("fk_dcim_device_role", type_="foreignkey")
        batch.drop_column("device_role_id")
    op.drop_table("dcim_device_roles")
