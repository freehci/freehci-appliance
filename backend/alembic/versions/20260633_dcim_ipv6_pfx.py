"""Record explicit IPv6 prefix on IP assignments so matching CIDR is never a link.

Revision ID: 20260633_dcim_ipv6_pfx
Revises: 20260632_dcim_port_iface
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260633_dcim_ipv6_pfx"
down_revision: Union[str, Sequence[str], None] = "20260632_dcim_port_iface"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dcim_interface_ip_assignments", sa.Column("ipv6_prefix_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_dcim_iface_ip_v6pfx",
        "dcim_interface_ip_assignments",
        "ipam_ipv6_prefixes",
        ["ipv6_prefix_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.add_column("dcim_device_ip_assignments", sa.Column("ipv6_prefix_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_dcim_dev_ip_v6pfx",
        "dcim_device_ip_assignments",
        "ipam_ipv6_prefixes",
        ["ipv6_prefix_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_dcim_dev_ip_v6pfx", "dcim_device_ip_assignments", type_="foreignkey")
    op.drop_column("dcim_device_ip_assignments", "ipv6_prefix_id")
    op.drop_constraint("fk_dcim_iface_ip_v6pfx", "dcim_interface_ip_assignments", type_="foreignkey")
    op.drop_column("dcim_interface_ip_assignments", "ipv6_prefix_id")
