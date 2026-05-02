"""DCIM component class inheritance and child templates.

Revision ID: 20260502_dcim_relations
Revises: 20260501_dcim_components
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260502_dcim_relations"
down_revision: Union[str, Sequence[str], None] = "20260501_dcim_components"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dcim_component_class_parents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("child_class_id", sa.Integer(), nullable=False),
        sa.Column("parent_class_id", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["child_class_id"], ["dcim_component_classes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_class_id"], ["dcim_component_classes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("child_class_id", "parent_class_id", name="uq_dcim_component_class_parent"),
    )
    op.create_index(
        "ix_dcim_component_class_parents_child",
        "dcim_component_class_parents",
        ["child_class_id"],
    )
    op.create_index(
        "ix_dcim_component_class_parents_parent",
        "dcim_component_class_parents",
        ["parent_class_id"],
    )

    op.create_table(
        "dcim_component_child_templates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("parent_component_id", sa.Integer(), nullable=False),
        sa.Column("child_class_id", sa.Integer(), nullable=False),
        sa.Column("child_component_id", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("name_pattern", sa.String(length=128), nullable=True),
        sa.Column("slot_label", sa.String(length=128), nullable=True),
        sa.Column("overrides_json", sa.JSON(), nullable=True),
        sa.Column("materialize_as", sa.String(length=32), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["parent_component_id"], ["dcim_components.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["child_class_id"], ["dcim_component_classes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["child_component_id"], ["dcim_components.id"], ondelete="SET NULL"),
    )
    op.create_index(
        "ix_dcim_component_child_templates_parent",
        "dcim_component_child_templates",
        ["parent_component_id"],
    )
    op.create_index(
        "ix_dcim_component_child_templates_child_class",
        "dcim_component_child_templates",
        ["child_class_id"],
    )
    op.create_index(
        "ix_dcim_component_child_templates_child_component",
        "dcim_component_child_templates",
        ["child_component_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_dcim_component_child_templates_child_component", table_name="dcim_component_child_templates")
    op.drop_index("ix_dcim_component_child_templates_child_class", table_name="dcim_component_child_templates")
    op.drop_index("ix_dcim_component_child_templates_parent", table_name="dcim_component_child_templates")
    op.drop_table("dcim_component_child_templates")
    op.drop_index("ix_dcim_component_class_parents_parent", table_name="dcim_component_class_parents")
    op.drop_index("ix_dcim_component_class_parents_child", table_name="dcim_component_class_parents")
    op.drop_table("dcim_component_class_parents")
