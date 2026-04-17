"""iam_roles_groups_and_user_identity_fields

Revision ID: 20260417_iam_rg
Revises: adfc3ca8cc4b
Create Date: 2026-04-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260417_iam_rg"
down_revision: Union[str, Sequence[str], None] = "adfc3ca8cc4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("external_subject_id", sa.String(length=512), nullable=True))
    op.add_column("users", sa.Column("identity_provider", sa.String(length=128), nullable=True))

    op.create_table(
        "iam_roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("system", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_iam_roles_name"),
        sa.UniqueConstraint("slug", name="uq_iam_roles_slug"),
    )

    op.create_table(
        "iam_groups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("external_subject_id", sa.String(length=512), nullable=True),
        sa.Column("identity_provider", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_iam_groups_name"),
        sa.UniqueConstraint("slug", name="uq_iam_groups_slug"),
    )

    op.create_table(
        "iam_group_users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["iam_groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("group_id", "user_id", name="uq_iam_group_users"),
    )

    op.create_table(
        "iam_group_subgroups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("child_group_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["child_group_id"], ["iam_groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["group_id"], ["iam_groups.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("group_id", "child_group_id", name="uq_iam_group_subgroups"),
    )

    op.create_table(
        "iam_user_roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["iam_roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "role_id", name="uq_iam_user_roles"),
    )


def downgrade() -> None:
    op.drop_table("iam_user_roles")
    op.drop_table("iam_group_subgroups")
    op.drop_table("iam_group_users")
    op.drop_table("iam_groups")
    op.drop_table("iam_roles")
    op.drop_column("users", "identity_provider")
    op.drop_column("users", "external_subject_id")
