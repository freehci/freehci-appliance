"""IPv4 prefixes scoped per DCIM site (overlapping CIDR across sites allowed).

Revision ID: 20260418_ipam_v4
Revises: 20260417_iface_vlan
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260418_ipam_v4"
down_revision: Union[str, Sequence[str], None] = "20260417_iface_vlan"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_ipv4_prefixes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cidr", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("site_id", "cidr", name="uq_ipam_ipv4_site_cidr"),
    )


def downgrade() -> None:
    op.drop_table("ipam_ipv4_prefixes")
