"""Record explicit interface LAG so membership is never inferred from name or speed.

Revision ID: 20260628_dcim_iface_lag
Revises: 20260627_ipam_vrf_stretch
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260628_dcim_iface_lag"
down_revision: Union[str, Sequence[str], None] = "20260627_ipam_vrf_stretch"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_device_interface_lags",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", "slug", name="uq_dcim_iface_lag_device_slug"),
    )
    op.create_table(
        "dcim_device_interface_lag_members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("lag_id", sa.Integer(), nullable=False),
        sa.Column("interface_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["lag_id"], ["dcim_device_interface_lags.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["interface_id"], ["dcim_device_interfaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("interface_id", name="uq_dcim_iface_lag_member_iface"),
        sa.UniqueConstraint("lag_id", "interface_id", name="uq_dcim_iface_lag_member_lag_iface"),
    )


def downgrade() -> None:
    op.drop_table("dcim_device_interface_lag_members")
    op.drop_table("dcim_device_interface_lags")
