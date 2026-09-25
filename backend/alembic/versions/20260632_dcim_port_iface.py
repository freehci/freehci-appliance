"""Record explicit port-to-interface so matching name is never a link.

Revision ID: 20260632_dcim_port_iface
Revises: 20260631_dcim_iface_vrf
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260632_dcim_port_iface"
down_revision: Union[str, Sequence[str], None] = "20260631_dcim_iface_vrf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dcim_device_ports", sa.Column("interface_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_dcim_port_iface",
        "dcim_device_ports",
        "dcim_device_interfaces",
        ["interface_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_unique_constraint("uq_dcim_device_port_iface", "dcim_device_ports", ["interface_id"])


def downgrade() -> None:
    op.drop_constraint("uq_dcim_device_port_iface", "dcim_device_ports", type_="unique")
    op.drop_constraint("fk_dcim_port_iface", "dcim_device_ports", type_="foreignkey")
    op.drop_column("dcim_device_ports", "interface_id")
