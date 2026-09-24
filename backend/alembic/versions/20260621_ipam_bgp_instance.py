"""Record a BGP process on a device without inventing neighbors, RIB or applying config.

Revision ID: 20260621_ipam_bgp_instance
Revises: 20260620_dcim_artifact_baseline
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260621_ipam_bgp_instance"
down_revision: Union[str, Sequence[str], None] = "20260620_dcim_artifact_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_bgp_instances",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("local_as_id", sa.Integer(), nullable=False),
        sa.Column("vrf_id", sa.Integer(), nullable=True),
        sa.Column("vrf_scope", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("intent", sa.String(length=32), nullable=False),
        sa.Column("router_id", sa.String(length=64), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["device_id"], ["dcim_device_instances.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["local_as_id"], ["ipam_autonomous_systems.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["vrf_id"], ["ipam_vrfs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_id", "local_as_id", "vrf_scope", name="uq_ipam_bgp_instance_device_as_vrf"),
        sa.UniqueConstraint("site_id", "slug", name="uq_ipam_bgp_instance_site_slug"),
    )
    with op.batch_alter_table("ipam_bgp_sessions") as batch_op:
        batch_op.add_column(sa.Column("bgp_instance_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_ipam_bgp_session_instance",
            "ipam_bgp_instances",
            ["bgp_instance_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("ipam_bgp_sessions") as batch_op:
        batch_op.drop_constraint("fk_ipam_bgp_session_instance", type_="foreignkey")
        batch_op.drop_column("bgp_instance_id")
    op.drop_table("ipam_bgp_instances")
