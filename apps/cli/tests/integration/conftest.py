import db.models  # noqa: F401 — registra todos los modelos en Base.metadata
import pytest
from db.base import Base
from sqlalchemy import create_engine
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as container:
        yield container


@pytest.fixture(scope="session")
def db_url(postgres_container):
    """Crea el schema una vez; devuelve la URL asyncpg."""
    sync_url = postgres_container.get_connection_url()
    engine = create_engine(sync_url)
    Base.metadata.create_all(engine)
    engine.dispose()
    return sync_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
