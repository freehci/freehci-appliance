"""Koble IPv4-prefiks til VLAN (valgfritt).

Revision ID: 20260433_ipam_prefix_vlan
Revises: 20260432_tenant_access
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260433_ipam_prefix_vlan"
down_revision: Union[str, Sequence[str], None] = "20260432_tenant_access"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ipam_ipv4_prefixes", sa.Column("vlan_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_ipam_ipv4_prefixes_vlan_id",
        "ipam_ipv4_prefixes",
        "ipam_vlans",
        ["vlan_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_ipam_ipv4_prefixes_vlan_id", "ipam_ipv4_prefixes", ["vlan_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ipam_ipv4_prefixes_vlan_id", table_name="ipam_ipv4_prefixes")
    op.drop_constraint("fk_ipam_ipv4_prefixes_vlan_id", "ipam_ipv4_prefixes", type_="foreignkey")
    op.drop_column("ipam_ipv4_prefixes", "vlan_id")

