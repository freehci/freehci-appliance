"""Add NetBox template normalization quality fields.

Revision ID: 20260507_netbox_template_quality
Revises: 20260506_netbox_dtl_import
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260507_netbox_template_quality"
down_revision: Union[str, Sequence[str], None] = "20260506_netbox_dtl_import"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("dcim_device_model_templates") as batch_op:
        batch_op.add_column(sa.Column("normalized_json", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("quality_score", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("quality_warnings_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("dcim_device_model_templates") as batch_op:
        batch_op.drop_column("quality_warnings_json")
        batch_op.drop_column("quality_score")
        batch_op.drop_column("normalized_json")
