"""Prefix role/status, VRF-scoped CIDR, VLAN/VRF slugs, address role.

Revision ID: 20260511_ipam_gitops
Revises: 20260510_ipam_prefix_slug
"""

from __future__ import annotations

import re
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260511_ipam_gitops"
down_revision: Union[str, Sequence[str], None] = "20260510_ipam_prefix_slug"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "item")[:128]


def _unique_slug(used: set[str], desired: str) -> str:
    base = _slugify(desired)
    candidate = base
    n = 2
    while candidate in used:
        suffix = f"-{n}"
        candidate = f"{base[: 128 - len(suffix)]}{suffix}"
        n += 1
    used.add(candidate)
    return candidate


def upgrade() -> None:
    with op.batch_alter_table("ipam_ipv4_prefixes") as batch_op:
        batch_op.add_column(sa.Column("vrf_scope", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("role", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("status", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))

    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE ipam_ipv4_prefixes SET "
            "vrf_scope = COALESCE(vrf_id, 0), "
            "role = COALESCE(role, 'active'), "
            "status = COALESCE(status, 'active'), "
            "updated_at = COALESCE(updated_at, created_at)"
        ),
    )

    with op.batch_alter_table("ipam_ipv4_prefixes") as batch_op:
        batch_op.alter_column("vrf_scope", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("role", existing_type=sa.String(length=32), nullable=False)
        batch_op.alter_column("status", existing_type=sa.String(length=32), nullable=False)
        batch_op.alter_column("updated_at", existing_type=sa.DateTime(timezone=True), nullable=False)
        batch_op.drop_constraint("uq_ipam_ipv4_site_cidr", type_="unique")
        batch_op.create_unique_constraint("uq_ipam_ipv4_site_vrf_cidr", ["site_id", "vrf_scope", "cidr"])

    with op.batch_alter_table("ipam_ipv4_addresses") as batch_op:
        batch_op.add_column(sa.Column("role", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("hostname", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("fqdn", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("dns_name", sa.String(length=255), nullable=True))

    conn.execute(sa.text("UPDATE ipam_ipv4_addresses SET role = COALESCE(role, 'host')"))

    with op.batch_alter_table("ipam_ipv4_addresses") as batch_op:
        batch_op.alter_column("role", existing_type=sa.String(length=32), nullable=False)

    with op.batch_alter_table("ipam_vrfs") as batch_op:
        batch_op.add_column(sa.Column("slug", sa.String(length=128), nullable=True))

    vrfs = list(conn.execute(sa.text("SELECT id, site_id, name FROM ipam_vrfs")))
    used_vrf: dict[int, set[str]] = {}
    for vid, site_id, name in vrfs:
        site_used = used_vrf.setdefault(int(site_id), set())
        slug = _unique_slug(site_used, str(name or f"vrf-{vid}"))
        conn.execute(sa.text("UPDATE ipam_vrfs SET slug = :slug WHERE id = :id"), {"slug": slug, "id": int(vid)})

    with op.batch_alter_table("ipam_vrfs") as batch_op:
        batch_op.alter_column("slug", existing_type=sa.String(length=128), nullable=False)
        batch_op.create_unique_constraint("uq_ipam_vrf_site_slug", ["site_id", "slug"])

    with op.batch_alter_table("ipam_vlans") as batch_op:
        batch_op.add_column(sa.Column("slug", sa.String(length=128), nullable=True))

    vlans = list(conn.execute(sa.text("SELECT id, site_id, vid, name FROM ipam_vlans")))
    used_vlan: dict[int, set[str]] = {}
    for lid, site_id, vid, name in vlans:
        site_used = used_vlan.setdefault(int(site_id), set())
        slug = _unique_slug(site_used, str(name or f"vlan-{vid}"))
        conn.execute(sa.text("UPDATE ipam_vlans SET slug = :slug WHERE id = :id"), {"slug": slug, "id": int(lid)})

    with op.batch_alter_table("ipam_vlans") as batch_op:
        batch_op.alter_column("slug", existing_type=sa.String(length=128), nullable=False)
        batch_op.create_unique_constraint("uq_ipam_vlan_site_slug", ["site_id", "slug"])


def downgrade() -> None:
    with op.batch_alter_table("ipam_vlans") as batch_op:
        batch_op.drop_constraint("uq_ipam_vlan_site_slug", type_="unique")
        batch_op.drop_column("slug")

    with op.batch_alter_table("ipam_vrfs") as batch_op:
        batch_op.drop_constraint("uq_ipam_vrf_site_slug", type_="unique")
        batch_op.drop_column("slug")

    with op.batch_alter_table("ipam_ipv4_addresses") as batch_op:
        batch_op.drop_column("dns_name")
        batch_op.drop_column("fqdn")
        batch_op.drop_column("hostname")
        batch_op.drop_column("role")

    with op.batch_alter_table("ipam_ipv4_prefixes") as batch_op:
        batch_op.drop_constraint("uq_ipam_ipv4_site_vrf_cidr", type_="unique")
        batch_op.create_unique_constraint("uq_ipam_ipv4_site_cidr", ["site_id", "cidr"])
        batch_op.drop_column("updated_at")
        batch_op.drop_column("status")
        batch_op.drop_column("role")
        batch_op.drop_column("vrf_scope")
