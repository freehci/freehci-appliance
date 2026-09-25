"""Record dual-stack groups so typed IDs or matching CIDRs never invent a pair.

Revision ID: 20260637_ipam_ds_grp
Revises: 20260636_ipam_gre
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260637_ipam_ds_grp"
down_revision: Union[str, Sequence[str], None] = "20260636_ipam_gre"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_dual_stack_groups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_ipam_dual_stack_group_slug"),
    )
    op.execute(
        sa.text(
            "UPDATE ipam_ipv4_prefixes SET dual_stack_group_id = NULL "
            "WHERE dual_stack_group_id IS NOT NULL "
            "AND dual_stack_group_id NOT IN (SELECT id FROM ipam_dual_stack_groups)",
        ),
    )
    op.execute(
        sa.text(
            "UPDATE ipam_ipv6_prefixes SET dual_stack_group_id = NULL "
            "WHERE dual_stack_group_id IS NOT NULL "
            "AND dual_stack_group_id NOT IN (SELECT id FROM ipam_dual_stack_groups)",
        ),
    )
    with op.batch_alter_table("ipam_ipv4_prefixes") as batch:
        batch.create_foreign_key(
            "fk_ipam_ipv4_ds_group",
            "ipam_dual_stack_groups",
            ["dual_stack_group_id"],
            ["id"],
            ondelete="SET NULL",
        )
    with op.batch_alter_table("ipam_ipv6_prefixes") as batch:
        batch.create_foreign_key(
            "fk_ipam_ipv6_ds_group",
            "ipam_dual_stack_groups",
            ["dual_stack_group_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("ipam_ipv6_prefixes") as batch:
        batch.drop_constraint("fk_ipam_ipv6_ds_group", type_="foreignkey")
    with op.batch_alter_table("ipam_ipv4_prefixes") as batch:
        batch.drop_constraint("fk_ipam_ipv4_ds_group", type_="foreignkey")
    op.drop_table("ipam_dual_stack_groups")
