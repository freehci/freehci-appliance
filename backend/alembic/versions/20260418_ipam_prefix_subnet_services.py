"""IPAM IPv4-prefiks: JSON for tjenester (gateway, DNS, DHCP m.m.).

Revision ID: ipam_pfx_subsvc
Revises: 20260417_iam_rg
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "ipam_pfx_subsvc"
down_revision: Union[str, Sequence[str], None] = "20260417_iam_rg"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ipam_ipv4_prefixes", sa.Column("subnet_services", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("ipam_ipv4_prefixes", "subnet_services")
