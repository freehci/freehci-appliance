"""Contract as a first-class provider object, without SLA.

Revision ID: 20260609_ipam_contract
Revises: 20260608_dcim_power_source
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260609_ipam_contract"
down_revision: Union[str, Sequence[str], None] = "20260608_dcim_power_source"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_contracts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=False),
        sa.Column("provider_account_id", sa.Integer(), nullable=True),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("reference", sa.String(length=128), nullable=True),
        sa.Column("starts_on", sa.Date(), nullable=True),
        sa.Column("ends_on", sa.Date(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["provider_id"], ["ipam_providers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["provider_account_id"], ["ipam_provider_accounts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider_id", "slug", name="uq_ipam_contract_provider_slug"),
    )
    with op.batch_alter_table("ipam_circuits") as batch_op:
        batch_op.add_column(sa.Column("contract_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_ipam_circuit_contract_id",
            "ipam_contracts",
            ["contract_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("ipam_circuits") as batch_op:
        batch_op.drop_constraint("fk_ipam_circuit_contract_id", type_="foreignkey")
        batch_op.drop_column("contract_id")
    op.drop_table("ipam_contracts")
