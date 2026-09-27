"""Record L2 domains so matching VIDs never invent membership.

Revision ID: 20260641_ipam_l2_dom
Revises: 20260640_ipam_addr_sp
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260641_ipam_l2_dom"
down_revision: Union[str, Sequence[str], None] = "20260640_ipam_addr_sp"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ipam_l2_domains",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_ipam_l2_domain_slug"),
    )
    with op.batch_alter_table("ipam_vlans") as batch:
        batch.add_column(sa.Column("l2_domain_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_ipam_vlan_l2_domain",
            "ipam_l2_domains",
            ["l2_domain_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("ipam_vlans") as batch:
        batch.drop_constraint("fk_ipam_vlan_l2_domain", type_="foreignkey")
        batch.drop_column("l2_domain_id")
    op.drop_table("ipam_l2_domains")
