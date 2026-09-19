"""Stable slugs for IPv4 prefixes (GitOps lookup by site + slug).

Revision ID: 20260510_ipam_prefix_slug
Revises: 20260509_iam_login_tokens
"""

from __future__ import annotations

import re
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260510_ipam_prefix_slug"
down_revision: Union[str, Sequence[str], None] = "20260509_iam_login_tokens"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").strip().lower()).strip("-")
    return (s or "prefix")[:128]


def upgrade() -> None:
    with op.batch_alter_table("ipam_ipv4_prefixes") as batch_op:
        batch_op.add_column(sa.Column("slug", sa.String(length=128), nullable=True))

    conn = op.get_bind()
    rows = list(conn.execute(sa.text("SELECT id, site_id, name, cidr FROM ipam_ipv4_prefixes")))
    used: dict[int, set[str]] = {}
    for pid, site_id, name, cidr in rows:
        base = _slugify(str(name or cidr or f"prefix-{pid}"))
        candidate = base
        n = 2
        site_used = used.setdefault(int(site_id), set())
        while candidate in site_used:
            suffix = f"-{n}"
            candidate = f"{base[: 128 - len(suffix)]}{suffix}"
            n += 1
        site_used.add(candidate)
        conn.execute(
            sa.text("UPDATE ipam_ipv4_prefixes SET slug = :slug WHERE id = :id"),
            {"slug": candidate, "id": int(pid)},
        )

    with op.batch_alter_table("ipam_ipv4_prefixes") as batch_op:
        batch_op.alter_column("slug", existing_type=sa.String(length=128), nullable=False)
        batch_op.create_unique_constraint("uq_ipam_ipv4_site_slug", ["site_id", "slug"])


def downgrade() -> None:
    with op.batch_alter_table("ipam_ipv4_prefixes") as batch_op:
        batch_op.drop_constraint("uq_ipam_ipv4_site_slug", type_="unique")
        batch_op.drop_column("slug")
