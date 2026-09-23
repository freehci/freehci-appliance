"""Record circuit capacity, CIR and provider circuit ID without measured load.

Revision ID: 20260611_ipam_circuit_capacity
Revises: 20260610_ipam_circuit_group
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260611_ipam_circuit_capacity"
down_revision: Union[str, Sequence[str], None] = "20260610_ipam_circuit_group"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("ipam_circuits") as batch_op:
        batch_op.add_column(sa.Column("provider_circuit_id", sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column("capacity_mbps", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("cir_mbps", sa.Integer(), nullable=True))
        batch_op.create_unique_constraint("uq_ipam_circuit_provider_cid", ["provider_id", "provider_circuit_id"])


def downgrade() -> None:
    with op.batch_alter_table("ipam_circuits") as batch_op:
        batch_op.drop_constraint("uq_ipam_circuit_provider_cid", type_="unique")
        batch_op.drop_column("cir_mbps")
        batch_op.drop_column("capacity_mbps")
        batch_op.drop_column("provider_circuit_id")
