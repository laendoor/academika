from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

import app.models  # noqa: F401 — registra todos los modelos en Base.metadata
from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.models.lkp_estado_academico import LkpEstadoAcademico
from app.models.lkp_estado_cursada import LkpEstadoCursada
from app.models.lkp_nivel_carrera import LkpNivelCarrera
from app.models.lkp_nucleo_carrera import LkpNucleoCarrera
from app.models.lkp_tipo_cursada import LkpTipoCursada
from app.models.lkp_user_role import LkpUserRole


def _seed_lkp(engine) -> None:
    """Inserta datos estáticos de lookup una vez para toda la sesión de tests."""
    with Session(engine) as session:
        session.add_all(
            [
                LkpEstadoAcademico(key="alumno_regular", label="Alumno Regular"),
                LkpEstadoAcademico(key="no_regular", label="No Regular"),
            ]
        )
        session.add_all(
            [
                LkpEstadoCursada(key="inscripto", code="I", label="Inscripto"),
                LkpEstadoCursada(key="regular", code="R", label="Regular"),
                LkpEstadoCursada(key="promocionado", code="P", label="Promocionado"),
                LkpEstadoCursada(key="aprobado", code="A", label="Aprobado"),
                LkpEstadoCursada(key="desaprobado", code="D", label="Desaprobado"),
                LkpEstadoCursada(key="pendiente_aprobacion", code="PA", label="Pendiente de Aprobación"),
            ]
        )
        session.add_all(
            [
                LkpTipoCursada(key="regular", label="Cursada Regular"),
                LkpTipoCursada(key="libre", label="Libre"),
            ]
        )
        session.add_all(
            [
                LkpUserRole(key="admin", label="Administrador"),
                LkpUserRole(key="director", label="Director de Carrera"),
            ]
        )
        session.add_all(
            [
                LkpNivelCarrera(key="grado", label="Grado"),
                LkpNivelCarrera(key="pregrado", label="Pregrado"),
            ]
        )
        session.add_all(
            [
                LkpNucleoCarrera(key="basico", label="Núcleo Básico"),
                LkpNucleoCarrera(key="avanzado", label="Núcleo Avanzado"),
                LkpNucleoCarrera(key="orientacion", label="Núcleo de Orientación"),
            ]
        )
        session.commit()


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16") as container:
        yield container


@pytest.fixture(scope="session")
def db_url(postgres_container):
    """Crea el schema y seedea lookups una vez; devuelve la URL asyncpg."""
    sync_url = postgres_container.get_connection_url()
    engine = create_engine(sync_url)
    Base.metadata.create_all(engine)
    _seed_lkp(engine)
    engine.dispose()
    return sync_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")


@pytest_asyncio.fixture
async def test_engine(db_url) -> AsyncGenerator[AsyncEngine]:
    """Engine NullPool compartido por db_session, client y clean_db dentro de un mismo test."""
    engine = create_async_engine(db_url, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(test_engine) -> async_sessionmaker:
    return async_sessionmaker(test_engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(session_factory) -> AsyncGenerator[AsyncSession]:
    """Cada test recibe su propia sesión con rollback al finalizar."""
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(autouse=True)
async def clean_db(test_engine: AsyncEngine) -> AsyncGenerator[None]:
    """Trunca tablas de negocio después de cada test. Las lkp son session-scoped y no se tocan."""
    yield
    async with AsyncSession(test_engine) as session:
        await session.execute(
            text(
                "TRUNCATE users, cursadas, planes_materias, alumno_carrera, alumnos,"
                " planes_de_estudio, correlativas, materias, carreras"
                " RESTART IDENTITY CASCADE"
            )
        )
        await session.commit()


@pytest_asyncio.fixture
async def client(session_factory) -> AsyncGenerator[AsyncClient]:
    """Cliente HTTP con sesión del mismo engine que el resto del test."""

    async def override_get_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
