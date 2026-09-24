"""Record extra interface VLAN members so trunk or tagged is never inferred from VID.

Revision ID: 20260630_dcim_if_vlan_mem
Revises: 20260629_dcim_iface_vlan
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260630_dcim_if_vlan_mem"
down_revision: Union[str, Sequence[str], None] = "20260629_dcim_iface_vlan"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_device_interface_vlan_members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("interface_id", sa.Integer(), nullable=False),
        sa.Column("ipam_vlan_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=True),
        sa.ForeignKeyConstraint(["interface_id"], ["dcim_device_interfaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ipam_vlan_id"], ["ipam_vlans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("interface_id", "ipam_vlan_id", name="uq_dcim_iface_vlan_member"),
    )


def downgrade() -> None:
    op.drop_table("dcim_device_interface_vlan_members")
