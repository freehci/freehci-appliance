"""dcim_site_address_roles_access_and_users

Revision ID: adfc3ca8cc4b
Revises: 20260430_dcim_enh
Create Date: 2026-04-17 10:51:20.954111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision: str = 'adfc3ca8cc4b'
down_revision: Union[str, Sequence[str], None] = '20260430_dcim_enh'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("dcim_sites", sa.Column("address_line1", sa.String(length=255), nullable=True))
    op.add_column("dcim_sites", sa.Column("address_line2", sa.String(length=255), nullable=True))
    op.add_column("dcim_sites", sa.Column("postal_code", sa.String(length=32), nullable=True))
    op.add_column("dcim_sites", sa.Column("city", sa.String(length=255), nullable=True))
    op.add_column("dcim_sites", sa.Column("county", sa.String(length=255), nullable=True))
    op.add_column("dcim_sites", sa.Column("country", sa.String(length=255), nullable=True))
    op.add_column("dcim_sites", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("dcim_sites", sa.Column("longitude", sa.Float(), nullable=True))
    op.add_column("dcim_sites", sa.Column("address_note", sa.Text(), nullable=True))

    op.add_column("users", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("phone", sa.String(length=64), nullable=True))
    op.add_column(
        "users",
        sa.Column("kind", sa.String(length=32), nullable=False, server_default=sa.text("'person'")),
    )
    op.add_column("users", sa.Column("notes", sa.Text(), nullable=True))

    op.create_table(
        "dcim_site_roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_dcim_site_role_name"),
        sa.UniqueConstraint("slug", name="uq_dcim_site_role_slug"),
    )

    op.create_table(
        "dcim_site_access",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("site_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("is_contact", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["role_id"], ["dcim_site_roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["site_id"], ["dcim_sites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("site_id", "user_id", "role_id", "is_contact", name="uq_dcim_site_access"),
    )


def downgrade() -> None:
    op.drop_table("dcim_site_access")
    op.drop_table("dcim_site_roles")

    op.drop_column("users", "notes")
    op.drop_column("users", "kind")
    op.drop_column("users", "phone")
    op.drop_column("users", "email")

    op.drop_column("dcim_sites", "address_note")
    op.drop_column("dcim_sites", "longitude")
    op.drop_column("dcim_sites", "latitude")
    op.drop_column("dcim_sites", "country")
    op.drop_column("dcim_sites", "county")
    op.drop_column("dcim_sites", "city")
    op.drop_column("dcim_sites", "postal_code")
    op.drop_column("dcim_sites", "address_line2")
    op.drop_column("dcim_sites", "address_line1")
