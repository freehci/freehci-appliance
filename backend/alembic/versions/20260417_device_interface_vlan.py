"""Optional 802.1Q VLAN ID on device interfaces.

Revision ID: 20260417_iface_vlan
Revises: 20260416_iface_ip
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260417_iface_vlan"
down_revision: Union[str, Sequence[str], None] = "20260416_iface_ip"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dcim_device_interfaces",
        sa.Column("vlan_id", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("dcim_device_interfaces", "vlan_id")
