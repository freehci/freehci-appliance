"""Record explicit interface-to-IPAM VLAN so matching VID is never membership.

Revision ID: 20260629_dcim_iface_vlan
Revises: 20260628_dcim_iface_lag
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260629_dcim_iface_vlan"
down_revision: Union[str, Sequence[str], None] = "20260628_dcim_iface_lag"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dcim_device_interfaces", sa.Column("ipam_vlan_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_dcim_iface_ipam_vlan",
        "dcim_device_interfaces",
        "ipam_vlans",
        ["ipam_vlan_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_dcim_iface_ipam_vlan", "dcim_device_interfaces", type_="foreignkey")
    op.drop_column("dcim_device_interfaces", "ipam_vlan_id")
