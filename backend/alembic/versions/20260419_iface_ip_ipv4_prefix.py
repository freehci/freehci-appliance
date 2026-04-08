"""Optional FK from interface IP assignment to IPv4 prefix (IPAM).

Revision ID: 20260419_iface_ip_pfx
Revises: 20260418_ipam_v4
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260419_iface_ip_pfx"
down_revision: Union[str, Sequence[str], None] = "20260418_ipam_v4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dcim_interface_ip_assignments",
        sa.Column("ipv4_prefix_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_dcim_iface_ip_ipv4_prefix",
        "dcim_interface_ip_assignments",
        "ipam_ipv4_prefixes",
        ["ipv4_prefix_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_dcim_iface_ip_ipv4_prefix", "dcim_interface_ip_assignments", type_="foreignkey")
    op.drop_column("dcim_interface_ip_assignments", "ipv4_prefix_id")
