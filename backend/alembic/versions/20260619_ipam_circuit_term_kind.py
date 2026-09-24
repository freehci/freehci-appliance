"""Record circuit termination kind without inferring unknown or provider-network.

Revision ID: 20260619_ipam_circuit_term_kind
Revises: 20260618_ipam_vpn_client_member
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260619_ipam_circuit_term_kind"
down_revision: Union[str, Sequence[str], None] = "20260618_ipam_vpn_client_member"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ipam_circuit_terminations", sa.Column("kind", sa.String(length=32), nullable=True))


def downgrade() -> None:
    op.drop_column("ipam_circuit_terminations", "kind")
