"""Record circuit ownership so leased or owned is never inferred from type or provider.

Revision ID: 20260622_ipam_circuit_ownership
Revises: 20260621_ipam_bgp_instance
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260622_ipam_circuit_ownership"
down_revision: Union[str, Sequence[str], None] = "20260621_ipam_bgp_instance"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("ipam_circuits") as batch_op:
        batch_op.add_column(sa.Column("ownership", sa.String(length=16), nullable=True))
    op.execute("UPDATE ipam_circuits SET ownership = 'leased' WHERE is_leased IS TRUE")


def downgrade() -> None:
    with op.batch_alter_table("ipam_circuits") as batch_op:
        batch_op.drop_column("ownership")
