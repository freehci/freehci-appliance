"""Add NetBox Device Type Library import catalog.

Revision ID: 20260506_netbox_dtl_import
Revises: 20260505_redfish_schema_bundles
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260506_netbox_dtl_import"
down_revision: Union[str, Sequence[str], None] = "20260505_redfish_schema_bundles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_netbox_dtl_imports",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("source_url", sa.String(length=1024), nullable=True),
        sa.Column("branch", sa.String(length=128), nullable=True),
        sa.Column("file_relpath", sa.String(length=512), nullable=False),
        sa.Column("extract_relpath", sa.String(length=512), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="ready"),
        sa.Column("item_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("manufacturer_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("image_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("component_template_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("sha256", name="uq_dcim_netbox_dtl_imports_sha256"),
    )
    op.create_index("ix_dcim_netbox_dtl_imports_created", "dcim_netbox_dtl_imports", ["created_at"])

    op.create_table(
        "dcim_netbox_dtl_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("import_id", sa.Integer(), nullable=False),
        sa.Column("manufacturer", sa.String(length=255), nullable=False),
        sa.Column("model", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("part_number", sa.String(length=128), nullable=True),
        sa.Column("u_height", sa.Float(), nullable=True),
        sa.Column("is_full_depth", sa.Boolean(), nullable=True),
        sa.Column("airflow", sa.String(length=64), nullable=True),
        sa.Column("front_image_relpath", sa.String(length=512), nullable=True),
        sa.Column("rear_image_relpath", sa.String(length=512), nullable=True),
        sa.Column("yaml_relpath", sa.String(length=512), nullable=False),
        sa.Column("component_counts_json", sa.JSON(), nullable=True),
        sa.Column("raw_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["import_id"], ["dcim_netbox_dtl_imports.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("import_id", "manufacturer", "slug", name="uq_dcim_netbox_dtl_item_import_slug"),
    )
    op.create_index("ix_dcim_netbox_dtl_items_import", "dcim_netbox_dtl_items", ["import_id"])
    op.create_index("ix_dcim_netbox_dtl_items_lookup", "dcim_netbox_dtl_items", ["manufacturer", "slug"])

    op.create_table(
        "dcim_device_model_templates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("device_model_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False, server_default="netbox_dtl"),
        sa.Column("component_type", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("raw_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["device_model_id"], ["dcim_device_models.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("device_model_id", "source", "component_type", "name", name="uq_dcim_device_model_template"),
    )
    op.create_index("ix_dcim_device_model_templates_model", "dcim_device_model_templates", ["device_model_id"])
    op.create_index("ix_dcim_device_model_templates_type", "dcim_device_model_templates", ["component_type"])


def downgrade() -> None:
    op.drop_index("ix_dcim_device_model_templates_type", table_name="dcim_device_model_templates")
    op.drop_index("ix_dcim_device_model_templates_model", table_name="dcim_device_model_templates")
    op.drop_table("dcim_device_model_templates")
    op.drop_index("ix_dcim_netbox_dtl_items_lookup", table_name="dcim_netbox_dtl_items")
    op.drop_index("ix_dcim_netbox_dtl_items_import", table_name="dcim_netbox_dtl_items")
    op.drop_table("dcim_netbox_dtl_items")
    op.drop_index("ix_dcim_netbox_dtl_imports_created", table_name="dcim_netbox_dtl_imports")
    op.drop_table("dcim_netbox_dtl_imports")
