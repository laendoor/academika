from sqlalchemy import ColumnElement, false, func
from sqlalchemy.orm import InstrumentedAttribute

# La migración de #115 tipea estas tres de nuevo, congeladas: una migración no
# puede cambiar de significado cuando cambie este módulo. Los modelos y el
# fixture de integración importan de acá.
F_UNACCENT_SQL = """
CREATE FUNCTION f_unaccent(text) RETURNS text
LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE
AS $$ SELECT public.unaccent('public.unaccent', $1) $$
"""

ALUMNO_SEARCH_TERM = "f_unaccent(lower(dni || ' ' || apellido || ' ' || nombre))"
MATERIA_SEARCH_TERM = "f_unaccent(lower(codigo || ' ' || coalesce(sigla, '') || ' ' || nombre))"

# Más tokens que esto no distingue nada y sí multiplica el costo de la query.
MAX_TOKENS = 8


def search_criteria(column: InstrumentedAttribute[str], term: str) -> list[ColumnElement[bool]]:
    """Un `AND` por token contra una columna normalizada: "luci fer" encuentra "Fernández Lucía"."""
    tokens = term.strip().split()[:MAX_TOKENS]
    if not tokens:
        # Un filtro sin texto no puede devolver todo como si hubiera filtrado.
        return [false()]
    return [column.like(func.f_unaccent(func.lower(f"%{_escape_like(t)}%")), escape="\\") for t in tokens]


def _escape_like(token: str) -> str:
    """Los comodines que escribe el usuario son texto, no operadores."""
    return token.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
