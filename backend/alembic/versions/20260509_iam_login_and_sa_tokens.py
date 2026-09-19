"""Link IAM users to login accounts; bind API tokens to service accounts.

Revision ID: 20260509_iam_login_tokens
Revises: 20260508_api_tokens
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260509_iam_login_tokens"
down_revision: Union[str, Sequence[str], None] = "20260508_api_tokens"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("admin_account_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_users_admin_account_id",
            "admin_accounts",
            ["admin_account_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_unique_constraint("uq_users_admin_account_id", ["admin_account_id"])

    with op.batch_alter_table("api_tokens") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_api_tokens_user_id",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    with op.batch_alter_table("api_tokens") as batch_op:
        batch_op.drop_constraint("fk_api_tokens_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("uq_users_admin_account_id", type_="unique")
        batch_op.drop_constraint("fk_users_admin_account_id", type_="foreignkey")
        batch_op.drop_column("admin_account_id")
