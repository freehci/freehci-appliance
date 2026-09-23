"""Record VPN site members without inventing hub-and-spoke from count.

Revision ID: 20260615_ipam_vpn_member
Revises: 20260614_ipam_tunnel_transport
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260615_ipam_vpn_member"
down_revision: Union[str, Sequence[str], None] = "20260614_ipam_tunnel_transport"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_vpn_members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("vpn_service_id", sa.Integer(), nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["vpn_service_id"], ["ipam_vpn_services.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("vpn_service_id", "site_id", name="uq_ipam_vpn_member_site"),
    )


def downgrade() -> None:
    op.drop_table("ipam_vpn_members")
