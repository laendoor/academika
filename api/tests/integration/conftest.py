import pytest
import pytest_asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

import app.models  # noqa: F401 — registra todos los modelos en Base.metadata
from app.db.base import Base
from app.models.lkp_academic_status import LkpAcademicStatus
from app.models.lkp_enrollment_status import LkpEnrollmentStatus
from app.models.lkp_enrollment_type import LkpEnrollmentType


def _seed_lkp(engine) -> None:
    """Inserta datos estáticos de lookup una vez para toda la sesión de tests."""
    with Session(engine) as session:
        session.add_all(
            [
                LkpAcademicStatus(key="alumno_regular", label="Alumno Regular"),
                LkpAcademicStatus(key="no_regular", label="No Regular"),
            ]
        )
        session.add_all(
            [
                LkpEnrollmentStatus(key="inscripto", code="I", label="Inscripto"),
                LkpEnrollmentStatus(key="regular", code="R", label="Regular"),
                LkpEnrollmentStatus(key="promocionado", code="P", label="Promocionado"),
                LkpEnrollmentStatus(key="aprobado", code="A", label="Aprobado"),
                LkpEnrollmentStatus(key="pendiente_aprobacion", code="PA", label="Pendiente de Aprobación"),
            ]
        )
        session.add_all(
            [
                LkpEnrollmentType(key="regular", label="Cursada Regular"),
                LkpEnrollmentType(key="libre", label="Libre"),
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
async def db_session(db_url) -> AsyncSession:
    """Cada test recibe su propio engine NullPool + sesión con rollback al finalizar."""
    engine = create_async_engine(db_url, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_db(db_session: AsyncSession) -> None:
    """Trunca tablas de negocio después de cada test. Las lkp son session-scoped y no se tocan."""
    yield
    await db_session.execute(
        text(
            "TRUNCATE course_enrollment, study_plan_course, student, study_plan, course, degree"
            " RESTART IDENTITY CASCADE"
        )
    )
    await db_session.commit()
