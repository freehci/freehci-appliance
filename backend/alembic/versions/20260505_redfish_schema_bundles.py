"""Add Redfish schema bundle catalog.

Revision ID: 20260505_redfish_schema_bundles
Revises: 20260504_dcim_identity_owners
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260505_redfish_schema_bundles"
down_revision: Union[str, Sequence[str], None] = "20260504_dcim_identity_owners"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_redfish_schema_bundles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=True),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("source_url", sa.String(length=1024), nullable=True),
        sa.Column("file_relpath", sa.String(length=512), nullable=False),
        sa.Column("extract_relpath", sa.String(length=512), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="ready"),
        sa.Column("schema_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("json_schema_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("csdl_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("openapi_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("dictionaries_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("sha256", name="uq_dcim_redfish_schema_bundles_sha256"),
    )
    op.create_index("ix_dcim_redfish_schema_bundles_created", "dcim_redfish_schema_bundles", ["created_at"])

    op.create_table(
        "dcim_redfish_schema_resources",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("bundle_id", sa.Integer(), nullable=False),
        sa.Column("resource_type", sa.String(length=128), nullable=False),
        sa.Column("schema_version", sa.String(length=64), nullable=True),
        sa.Column("schema_uri", sa.String(length=512), nullable=False),
        sa.Column("format", sa.String(length=32), nullable=False),
        sa.Column("file_relpath", sa.String(length=512), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["bundle_id"], ["dcim_redfish_schema_bundles.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("bundle_id", "format", "schema_uri", name="uq_dcim_redfish_schema_resource_uri"),
    )
    op.create_index("ix_dcim_redfish_schema_resources_bundle", "dcim_redfish_schema_resources", ["bundle_id"])
    op.create_index("ix_dcim_redfish_schema_resources_lookup", "dcim_redfish_schema_resources", ["resource_type", "format"])


def downgrade() -> None:
    op.drop_index("ix_dcim_redfish_schema_resources_lookup", table_name="dcim_redfish_schema_resources")
    op.drop_index("ix_dcim_redfish_schema_resources_bundle", table_name="dcim_redfish_schema_resources")
    op.drop_table("dcim_redfish_schema_resources")
    op.drop_index("ix_dcim_redfish_schema_bundles_created", table_name="dcim_redfish_schema_bundles")
    op.drop_table("dcim_redfish_schema_bundles")
