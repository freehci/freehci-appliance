"""Integration connections, device identities and conflicts.

Revision ID: 20260525_integration
Revises: 20260524_dcim_power
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260525_integration"
down_revision: Union[str, Sequence[str], None] = "20260524_dcim_power"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "integration_connections",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("plugin_id", sa.String(length=128), nullable=False),
        sa.Column("base_url", sa.String(length=1024), nullable=True),
        sa.Column("credential_ref", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="planned"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("mapping_json", sa.JSON(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_integration_connection_slug"),
    )
    op.create_table(
        "dcim_device_identities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("identity_type", sa.String(length=32), nullable=False),
        sa.Column("namespace", sa.String(length=64), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("normalized_value", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("identity_type", "namespace", "normalized_value", name="uq_dcim_device_identity_value"),
    )
    op.create_table(
        "dcim_device_identity_claims",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("identity_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["connection_id"], ["integration_connections.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["identity_id"], ["dcim_device_identities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("connection_id", "identity_id", name="uq_dcim_device_identity_claim"),
    )
    op.create_table(
        "integration_identity_conflicts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("identity_type", sa.String(length=32), nullable=False),
        sa.Column("namespace", sa.String(length=64), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("normalized_value", sa.String(length=255), nullable=False),
        sa.Column("connection_a_id", sa.Integer(), nullable=True),
        sa.Column("connection_b_id", sa.Integer(), nullable=True),
        sa.Column("device_a_id", sa.Integer(), nullable=True),
        sa.Column("device_b_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["connection_a_id"], ["integration_connections.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["connection_b_id"], ["integration_connections.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["device_a_id"], ["dcim_device_instances.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["device_b_id"], ["dcim_device_instances.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "identity_type",
            "namespace",
            "normalized_value",
            "device_a_id",
            "device_b_id",
            name="uq_integration_identity_conflict",
        ),
    )


def downgrade() -> None:
    op.drop_table("integration_identity_conflicts")
    op.drop_table("dcim_device_identity_claims")
    op.drop_table("dcim_device_identities")
    op.drop_table("integration_connections")
