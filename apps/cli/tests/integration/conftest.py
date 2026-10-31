import db.models  # noqa: F401 — registra todos los modelos en Base.metadata
import pytest
import pytest_asyncio
from db.base import Base
from db.search import F_UNACCENT_SQL
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer


def _create_search_helpers(engine) -> None:
    """f_unaccent() no viene con el schema y las columnas search_term la generan."""
    with Session(engine) as session:
        session.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent"))
        session.execute(text(F_UNACCENT_SQL))
        session.commit()


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as container:
        yield container


@pytest.fixture(scope="session")
def db_url(postgres_container):
    """Crea el schema una vez; devuelve la URL asyncpg."""
    sync_url = postgres_container.get_connection_url()
    engine = create_engine(sync_url)
    _create_search_helpers(engine)
    Base.metadata.create_all(engine)
    engine.dispose()
    return sync_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")


@pytest_asyncio.fixture
async def session_factory(db_url):
    """NullPool: cada test corre en su propio loop y un pool ataría conexiones al anterior."""
    engine = create_async_engine(db_url, poolclass=NullPool)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()
