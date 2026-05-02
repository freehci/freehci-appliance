"""DCIM component identity registry.

Revision ID: 20260503_dcim_identities
Revises: 20260502_dcim_relations
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260503_dcim_identities"
down_revision: Union[str, Sequence[str], None] = "20260502_dcim_relations"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_component_identities",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("component_id", sa.Integer(), nullable=False),
        sa.Column("manufacturer_id", sa.Integer(), nullable=True),
        sa.Column("identity_type", sa.String(length=32), nullable=False),
        sa.Column("namespace", sa.String(length=64), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("normalized_value", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=True),
        sa.Column("confidence", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("raw_json", sa.JSON(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["component_id"], ["dcim_components.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["manufacturer_id"], ["dcim_manufacturers.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("identity_type", "namespace", "normalized_value", name="uq_dcim_component_identity_value"),
    )
    op.create_index("ix_dcim_component_identities_component", "dcim_component_identities", ["component_id"])
    op.create_index("ix_dcim_component_identities_mfr", "dcim_component_identities", ["manufacturer_id"])
    op.create_index(
        "ix_dcim_component_identities_lookup",
        "dcim_component_identities",
        ["identity_type", "namespace", "normalized_value"],
    )


def downgrade() -> None:
    op.drop_index("ix_dcim_component_identities_lookup", table_name="dcim_component_identities")
    op.drop_index("ix_dcim_component_identities_mfr", table_name="dcim_component_identities")
    op.drop_index("ix_dcim_component_identities_component", table_name="dcim_component_identities")
    op.drop_table("dcim_component_identities")
