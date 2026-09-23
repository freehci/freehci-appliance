"""Circuit redundancy group without claimed independence.

Revision ID: 20260610_ipam_circuit_group
Revises: 20260609_ipam_contract
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260610_ipam_circuit_group"
down_revision: Union[str, Sequence[str], None] = "20260609_ipam_contract"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_circuit_groups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("tenant_scope", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("shared_risk", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_scope", "slug", name="uq_ipam_circuit_group_tenant_scope_slug"),
    )
    with op.batch_alter_table("ipam_circuits") as batch_op:
        batch_op.add_column(sa.Column("group_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_ipam_circuit_group_id",
            "ipam_circuit_groups",
            ["group_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("ipam_circuits") as batch_op:
        batch_op.drop_constraint("fk_ipam_circuit_group_id", type_="foreignkey")
        batch_op.drop_column("group_id")
    op.drop_table("ipam_circuit_groups")
