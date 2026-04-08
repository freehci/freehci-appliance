"""IPv4/IPv6 assignments per device interface (IPAM-forberedelse).

Revision ID: 20260416_iface_ip
Revises: 20260415_ifaces
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260416_iface_ip"
down_revision: Union[str, Sequence[str], None] = "20260415_ifaces"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_interface_ip_assignments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("interface_id", sa.Integer(), nullable=False),
        sa.Column("family", sa.String(length=4), nullable=False),
        sa.Column("address", sa.String(length=45), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["interface_id"], ["dcim_device_interfaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("interface_id", "address", name="uq_dcim_iface_ip_addr"),
    )


def downgrade() -> None:
    op.drop_table("dcim_interface_ip_assignments")
