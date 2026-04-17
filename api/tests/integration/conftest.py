import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

import app.models  # noqa: F401 — registra todos los modelos en Base.metadata
from app.db.base import Base


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as container:
        yield container


@pytest.fixture(scope="session")
def db_url(postgres_container):
    """Crea el schema una vez usando psycopg2 (sync) y devuelve la URL asyncpg."""
    sync_url = postgres_container.get_connection_url()
    engine = create_engine(sync_url)
    Base.metadata.create_all(engine)
    engine.dispose()
    return sync_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")


@pytest_asyncio.fixture
async def db_session(db_url) -> AsyncSession:
    """Cada test recibe su propio engine NullPool + sesión con rollback al finalizar."""
    engine = create_async_engine(db_url, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()
    await engine.dispose()
