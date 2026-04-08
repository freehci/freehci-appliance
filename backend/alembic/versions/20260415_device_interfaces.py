"""Physical / logical interfaces (ports) on device instances.

Revision ID: 20260415_ifaces
Revises: 20260414_device_types
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260415_ifaces"
down_revision: Union[str, Sequence[str], None] = "20260414_device_types"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_device_interfaces",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("mac_address", sa.String(length=32), nullable=True),
        sa.Column("speed_mbps", sa.Integer(), nullable=True),
        sa.Column("mtu", sa.Integer(), nullable=True),
        # PostgreSQL: boolean default must be true/false, not integer 1/0.
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", "name", name="uq_dcim_device_interface_device_name"),
    )


def downgrade() -> None:
    op.drop_table("dcim_device_interfaces")
