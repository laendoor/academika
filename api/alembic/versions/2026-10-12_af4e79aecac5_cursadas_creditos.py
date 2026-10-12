"""Agrega columna creditos a cursadas (importador historial Guaraní, #68)."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "af4e79aecac5"
down_revision: str | Sequence[str] | None = "5293fcf210fc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("cursadas", sa.Column("creditos", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("cursadas", "creditos")
