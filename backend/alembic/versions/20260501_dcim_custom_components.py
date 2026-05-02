"""DCIM custom hardware components.

Revision ID: 20260501_dcim_components
Revises: 20260434_ipam_prefix_vrf
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260501_dcim_components"
down_revision: Union[str, Sequence[str], None] = "20260434_ipam_prefix_vrf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_component_classes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(length=64), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("name", name="uq_dcim_component_classes_name"),
        sa.UniqueConstraint("slug", name="uq_dcim_component_classes_slug"),
    )
    op.create_table(
        "dcim_component_class_fields",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("data_type", sa.String(length=16), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=True),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("min_number", sa.Float(), nullable=True),
        sa.Column("max_number", sa.Float(), nullable=True),
        sa.Column("choices_json", sa.JSON(), nullable=True),
        sa.Column("default_value", sa.JSON(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["class_id"], ["dcim_component_classes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("class_id", "key", name="uq_dcim_component_class_fields_class_key"),
    )
    op.create_index("ix_dcim_component_class_fields_class_id", "dcim_component_class_fields", ["class_id"])

    op.create_table(
        "dcim_components",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("manufacturer_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("part_number", sa.String(length=128), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("specs_json", sa.JSON(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["class_id"], ["dcim_component_classes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["manufacturer_id"], ["dcim_manufacturers.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("class_id", "manufacturer_id", "part_number", name="uq_dcim_components_class_mfr_part"),
    )
    op.create_index("ix_dcim_components_class_id", "dcim_components", ["class_id"])
    op.create_index("ix_dcim_components_manufacturer_id", "dcim_components", ["manufacturer_id"])

    op.create_table(
        "dcim_device_model_components",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("device_model_id", sa.Integer(), nullable=False),
        sa.Column("component_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("slot_label", sa.String(length=128), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("overrides_json", sa.JSON(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["device_model_id"], ["dcim_device_models.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["component_id"], ["dcim_components.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_dcim_device_model_components_model_id", "dcim_device_model_components", ["device_model_id"])
    op.create_index("ix_dcim_device_model_components_component_id", "dcim_device_model_components", ["component_id"])

    op.create_table(
        "dcim_device_instance_components",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("component_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("slot_label", sa.String(length=128), nullable=True),
        sa.Column("serial_number", sa.String(length=128), nullable=True),
        sa.Column("asset_tag", sa.String(length=128), nullable=True),
        sa.Column("installed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("overrides_json", sa.JSON(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["component_id"], ["dcim_components.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_dcim_device_instance_components_device_id", "dcim_device_instance_components", ["device_id"])
    op.create_index("ix_dcim_device_instance_components_component_id", "dcim_device_instance_components", ["component_id"])


def downgrade() -> None:
    op.drop_index("ix_dcim_device_instance_components_component_id", table_name="dcim_device_instance_components")
    op.drop_index("ix_dcim_device_instance_components_device_id", table_name="dcim_device_instance_components")
    op.drop_table("dcim_device_instance_components")
    op.drop_index("ix_dcim_device_model_components_component_id", table_name="dcim_device_model_components")
    op.drop_index("ix_dcim_device_model_components_model_id", table_name="dcim_device_model_components")
    op.drop_table("dcim_device_model_components")
    op.drop_index("ix_dcim_components_manufacturer_id", table_name="dcim_components")
    op.drop_index("ix_dcim_components_class_id", table_name="dcim_components")
    op.drop_table("dcim_components")
    op.drop_index("ix_dcim_component_class_fields_class_id", table_name="dcim_component_class_fields")
    op.drop_table("dcim_component_class_fields")
    op.drop_table("dcim_component_classes")
