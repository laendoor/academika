"""Agrega columna area a materias (desglose de avance por área, #96).

Revision ID: f754707ed22b
Revises: b811fa1e71b6
Create Date: 2026-11-07 12:44:36.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f754707ed22b"
down_revision: str | Sequence[str] | None = "b811fa1e71b6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("materias", sa.Column("area", sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column("materias", "area")
