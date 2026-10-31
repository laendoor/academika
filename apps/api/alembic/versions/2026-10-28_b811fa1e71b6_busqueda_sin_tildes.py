"""Búsqueda sin tildes ni ñ: extensiones, wrapper inmutable y columnas search_term (#115).

Revision ID: b811fa1e71b6
Revises: af4e79aecac5
Create Date: 2026-10-28 21:12:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b811fa1e71b6"
down_revision: str | Sequence[str] | None = "af4e79aecac5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# unaccent() es STABLE (depende del diccionario en disco), así que Postgres no deja
# usarla en una columna generada. El wrapper la declara IMMUTABLE y es la única
# expresión que el código usa, tanto en las columnas como en las queries.
_F_UNACCENT = """
CREATE FUNCTION f_unaccent(text) RETURNS text
LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE
AS $$ SELECT public.unaccent('public.unaccent', $1) $$
"""

# Congeladas a propósito: copian las de db.search y no se importan, para que esta
# migración no cambie de significado si esas constantes cambian.
_ALUMNOS_SEARCH_TERM = "f_unaccent(lower(dni || ' ' || apellido || ' ' || nombre))"
_MATERIAS_SEARCH_TERM = "f_unaccent(lower(codigo || ' ' || coalesce(sigla, '') || ' ' || nombre))"


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    op.execute(_F_UNACCENT)

    op.execute(f"ALTER TABLE alumnos ADD COLUMN search_term text GENERATED ALWAYS AS ({_ALUMNOS_SEARCH_TERM}) STORED")
    op.execute(f"ALTER TABLE materias ADD COLUMN search_term text GENERATED ALWAYS AS ({_MATERIAS_SEARCH_TERM}) STORED")


def downgrade() -> None:
    op.execute("ALTER TABLE materias DROP COLUMN search_term")
    op.execute("ALTER TABLE alumnos DROP COLUMN search_term")
    op.execute("DROP FUNCTION f_unaccent(text)")
    # Las extensiones no se dropean: pueden estar en uso por otra cosa del mismo cluster.
