import pytest
from lyka.render import render_result
from lyka.session import ConfigError, database_url, get_session_factory
from rich.table import Table
from sqlalchemy.ext.asyncio import async_sessionmaker


def headers(table: Table) -> list[str]:
    return [column.header for column in table.columns]


def test_dict_a_tabla_campo_valor():
    output = render_result({"ok": True})
    assert isinstance(output, Table)
    assert headers(output) == ["campo", "valor"]
    assert output.row_count == 1


def test_lista_de_dicts_a_tabla_con_columnas():
    output = render_result([{"key": "smoke", "name": "Smoke"}, {"key": "m2", "name": "M2", "extra": 1}])
    assert isinstance(output, Table)
    assert headers(output) == ["key", "name", "extra"]
    assert output.row_count == 2


def test_escalar_a_texto():
    assert render_result(42).plain == "42"


def test_falta_database_url_falla_claro(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ConfigError, match="DATABASE_URL"):
        database_url()


def test_database_url_normaliza_scheme(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost:5432/db")
    assert database_url() == "postgresql+asyncpg://u:p@localhost:5432/db"


def test_session_factory_no_conecta_al_crearla(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db")
    assert isinstance(get_session_factory(), async_sessionmaker)
