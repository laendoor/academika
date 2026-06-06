"""add_users_table

Revision ID: d33b3d18dbb1
Revises: e22a6112a67a
Create Date: 2026-05-30 22:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d33b3d18dbb1"
down_revision: str | Sequence[str] | None = "e22a6112a67a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "lkp_user_roles",
        sa.Column("key", sa.String(50), primary_key=True),
        sa.Column("label", sa.String(100), nullable=False),
    )
    op.bulk_insert(
        sa.table(
            "lkp_user_roles",
            sa.column("key", sa.String),
            sa.column("label", sa.String),
        ),
        [
            {"key": "admin", "label": "Administrador"},
            {"key": "director", "label": "Director de Carrera"},
        ],
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(native_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), sa.ForeignKey("lkp_user_roles.key"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("lkp_user_roles")
