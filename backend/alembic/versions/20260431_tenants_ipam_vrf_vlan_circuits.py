"""Tenants, site.tenant_id, IPAM VRF/VLAN og samband (circuits).

Revision ID: 20260431_tenant_ipam
Revises: 20260430_dcim_enh
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260431_tenant_ipam"
down_revision: Union[str, Sequence[str], None] = "20260430_dcim_enh"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.execute(
        sa.text(
            "INSERT INTO tenants (name, slug, description) VALUES ('Default', 'default', 'Migrert innhold')",
        ),
    )

    op.add_column(
        "dcim_sites",
        sa.Column("tenant_id", sa.Integer(), server_default="1", nullable=False),
    )
    op.create_foreign_key(
        "fk_dcim_sites_tenant_id",
        "dcim_sites",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.create_table(
        "ipam_vrfs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("route_distinguisher", sa.String(length=64), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("site_id", "name", name="uq_ipam_vrf_site_name"),
    )

    op.create_table(
        "ipam_vlans",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("vid", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("vrf_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vrf_id"], ["ipam_vrfs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("site_id", "vid", name="uq_ipam_vlan_site_vid"),
    )

    op.create_table(
        "ipam_circuits",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("circuit_number", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("circuit_type", sa.String(length=32), nullable=False),
        sa.Column("is_leased", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("provider_name", sa.String(length=255), nullable=True),
        sa.Column("established_on", sa.Date(), nullable=True),
        sa.Column("contract_end_on", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "circuit_number", name="uq_ipam_circuit_tenant_number"),
    )

    op.create_table(
        "ipam_circuit_terminations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("circuit_id", sa.Integer(), nullable=False),
        sa.Column("endpoint", sa.String(length=1), nullable=False),
        sa.Column("interface_id", sa.Integer(), nullable=True),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["circuit_id"], ["ipam_circuits.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["interface_id"], ["dcim_device_interfaces.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("circuit_id", "endpoint", name="uq_ipam_circuit_term_endpoint"),
    )


def downgrade() -> None:
    op.drop_table("ipam_circuit_terminations")
    op.drop_table("ipam_circuits")
    op.drop_table("ipam_vlans")
    op.drop_table("ipam_vrfs")
    op.drop_constraint("fk_dcim_sites_tenant_id", "dcim_sites", type_="foreignkey")
    op.drop_column("dcim_sites", "tenant_id")
    op.drop_table("tenants")
