"""IPv6 grid/split/scan: subnet-scan kan peke på IPv6-prefiks.

Revision ID: 20260515_ipam_ipv6_grid
Revises: 20260514_ipam_sync
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260515_ipam_ipv6_grid"
down_revision: Union[str, Sequence[str], None] = "20260514_ipam_sync"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ipam_subnet_scans", sa.Column("ipv6_prefix_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_ipam_subnet_scans_ipv6_prefix_id",
        "ipam_subnet_scans",
        "ipam_ipv6_prefixes",
        ["ipv6_prefix_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.alter_column(
        "ipam_subnet_scans",
        "cidr",
        existing_type=sa.String(length=32),
        type_=sa.String(length=64),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "ipam_subnet_scans",
        "cidr",
        existing_type=sa.String(length=64),
        type_=sa.String(length=32),
        existing_nullable=False,
    )
    op.drop_constraint("fk_ipam_subnet_scans_ipv6_prefix_id", "ipam_subnet_scans", type_="foreignkey")
    op.drop_column("ipam_subnet_scans", "ipv6_prefix_id")
