"""Record GRE profiles without inventing encryption, endpoints or keys.

Revision ID: 20260636_ipam_gre
Revises: 20260635_ipam_ipsec
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260636_ipam_gre"
down_revision: Union[str, Sequence[str], None] = "20260635_ipam_ipsec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_gre_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("local_address", sa.String(length=64), nullable=True),
        sa.Column("remote_address", sa.String(length=64), nullable=True),
        sa.Column("key_id", sa.BigInteger(), nullable=True),
        sa.Column("ttl", sa.Integer(), nullable=True),
        sa.Column("checksum", sa.Boolean(), nullable=True),
        sa.Column("sequence", sa.Boolean(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_ipam_gre_profile_slug"),
    )
    op.create_table(
        "ipam_gre_tunnels",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tunnel_id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["tunnel_id"], ["ipam_tunnels.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["profile_id"], ["ipam_gre_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tunnel_id", name="uq_ipam_gre_tunnel"),
    )


def downgrade() -> None:
    op.drop_table("ipam_gre_tunnels")
    op.drop_table("ipam_gre_profiles")
