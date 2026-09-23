"""Bind tunnels to underlay circuits without inventing failover.

Revision ID: 20260614_ipam_tunnel_transport
Revises: 20260613_ipam_circuit_strand
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260614_ipam_tunnel_transport"
down_revision: Union[str, Sequence[str], None] = "20260613_ipam_circuit_strand"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_tunnel_transports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tunnel_id", sa.Integer(), nullable=False),
        sa.Column("circuit_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["tunnel_id"], ["ipam_tunnels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["circuit_id"], ["ipam_circuits.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tunnel_id", "circuit_id", name="uq_ipam_tunnel_transport_circuit"),
    )


def downgrade() -> None:
    op.drop_table("ipam_tunnel_transports")
