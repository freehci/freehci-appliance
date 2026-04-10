"""Admin accounts for UI/API login.

Revision ID: 20260424_admin_acc
Revises: 20260422_iface_parent
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260424_admin_acc"
down_revision: Union[str, Sequence[str], None] = "20260422_iface_parent"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin_accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=128), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uq_admin_accounts_username"),
    )


def downgrade() -> None:
    op.drop_table("admin_accounts")
