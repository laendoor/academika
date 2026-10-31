import pytest
from clika.session import ConfigError, database_url, get_session_factory
from sqlalchemy.ext.asyncio import async_sessionmaker


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
