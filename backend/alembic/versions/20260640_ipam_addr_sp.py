"""Record address spaces so matching CIDRs never invent a shared plan.

Revision ID: 20260640_ipam_addr_sp
Revises: 20260639_int_own_map
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260640_ipam_addr_sp"
down_revision: Union[str, Sequence[str], None] = "20260639_int_own_map"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_address_spaces",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_ipam_address_space_slug"),
    )
    with op.batch_alter_table("ipam_ipv4_prefixes") as batch:
        batch.add_column(sa.Column("address_space_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_ipam_ipv4_addr_space",
            "ipam_address_spaces",
            ["address_space_id"],
            ["id"],
            ondelete="SET NULL",
        )
    with op.batch_alter_table("ipam_ipv6_prefixes") as batch:
        batch.add_column(sa.Column("address_space_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_ipam_ipv6_addr_space",
            "ipam_address_spaces",
            ["address_space_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("ipam_ipv6_prefixes") as batch:
        batch.drop_constraint("fk_ipam_ipv6_addr_space", type_="foreignkey")
        batch.drop_column("address_space_id")
    with op.batch_alter_table("ipam_ipv4_prefixes") as batch:
        batch.drop_constraint("fk_ipam_ipv4_addr_space", type_="foreignkey")
        batch.drop_column("address_space_id")
    op.drop_table("ipam_address_spaces")
