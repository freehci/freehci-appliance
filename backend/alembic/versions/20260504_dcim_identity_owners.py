"""Normalize DCIM identity owners.

Revision ID: 20260504_dcim_identity_owners
Revises: 20260503_dcim_identities
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260504_dcim_identity_owners"
down_revision: Union[str, Sequence[str], None] = "20260503_dcim_identities"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_manufacturer_identities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("manufacturer_id", sa.Integer(), nullable=False),
        sa.Column("identity_type", sa.String(length=32), nullable=False),
        sa.Column("namespace", sa.String(length=64), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("normalized_value", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=True),
        sa.Column("confidence", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("raw_json", sa.JSON(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["manufacturer_id"], ["dcim_manufacturers.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("identity_type", "namespace", "normalized_value", name="uq_dcim_manufacturer_identity_value"),
    )
    op.create_index("ix_dcim_manufacturer_identities_mfr", "dcim_manufacturer_identities", ["manufacturer_id"])
    op.create_index(
        "ix_dcim_manufacturer_identities_lookup",
        "dcim_manufacturer_identities",
        ["identity_type", "namespace", "normalized_value"],
    )

    op.create_table(
        "dcim_device_model_identities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("device_model_id", sa.Integer(), nullable=False),
        sa.Column("identity_type", sa.String(length=32), nullable=False),
        sa.Column("namespace", sa.String(length=64), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("normalized_value", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=True),
        sa.Column("confidence", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("raw_json", sa.JSON(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["device_model_id"], ["dcim_device_models.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("identity_type", "namespace", "normalized_value", name="uq_dcim_device_model_identity_value"),
    )
    op.create_index("ix_dcim_device_model_identities_model", "dcim_device_model_identities", ["device_model_id"])
    op.create_index(
        "ix_dcim_device_model_identities_lookup",
        "dcim_device_model_identities",
        ["identity_type", "namespace", "normalized_value"],
    )

    op.drop_index("ix_dcim_component_identities_mfr", table_name="dcim_component_identities")
    with op.batch_alter_table("dcim_component_identities") as batch_op:
        batch_op.drop_column("manufacturer_id")


def downgrade() -> None:
    with op.batch_alter_table("dcim_component_identities") as batch_op:
        batch_op.add_column(sa.Column("manufacturer_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_dcim_component_identities_manufacturer_id",
            "dcim_manufacturers",
            ["manufacturer_id"],
            ["id"],
            ondelete="SET NULL",
        )
    op.create_index("ix_dcim_component_identities_mfr", "dcim_component_identities", ["manufacturer_id"])

    op.drop_index("ix_dcim_device_model_identities_lookup", table_name="dcim_device_model_identities")
    op.drop_index("ix_dcim_device_model_identities_model", table_name="dcim_device_model_identities")
    op.drop_table("dcim_device_model_identities")
    op.drop_index("ix_dcim_manufacturer_identities_lookup", table_name="dcim_manufacturer_identities")
    op.drop_index("ix_dcim_manufacturer_identities_mfr", table_name="dcim_manufacturer_identities")
    op.drop_table("dcim_manufacturer_identities")
