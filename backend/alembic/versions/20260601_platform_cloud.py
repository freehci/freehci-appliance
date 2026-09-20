"""Skyabonnement uten oppfunnet kostnad eller kvote.

Revision ID: 20260601_platform_cloud
Revises: 20260531_platform_disk
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260601_platform_cloud"
down_revision: Union[str, Sequence[str], None] = "20260531_platform_disk"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_cloud_subscriptions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False, server_default="other"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="planned"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_platform_cloud_slug"),
    )
    with op.batch_alter_table("catalog_service_deployments") as batch:
        batch.add_column(sa.Column("cloud_subscription_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_catalog_deployment_cloud",
            "platform_cloud_subscriptions",
            ["cloud_subscription_id"],
            ["id"],
            ondelete="SET NULL",
        )
    with op.batch_alter_table("catalog_service_instances") as batch:
        batch.add_column(sa.Column("cloud_subscription_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_catalog_instance_cloud",
            "platform_cloud_subscriptions",
            ["cloud_subscription_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("catalog_service_instances") as batch:
        batch.drop_constraint("fk_catalog_instance_cloud", type_="foreignkey")
        batch.drop_column("cloud_subscription_id")
    with op.batch_alter_table("catalog_service_deployments") as batch:
        batch.drop_constraint("fk_catalog_deployment_cloud", type_="foreignkey")
        batch.drop_column("cloud_subscription_id")
    op.drop_table("platform_cloud_subscriptions")
