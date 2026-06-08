from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import generate_uuid
from app.models.alumno import Alumno
from app.models.carrera import Carrera
from app.models.cursada import Cursada
from app.models.materia import Materia
from app.models.plan_de_estudio import PlanDeEstudio
from app.services.guarani_importer import GuaraniImporterService

SAMPLE_DATA = Path(__file__).parents[3] / "sample-data"


async def _seed(session: AsyncSession) -> None:
    tpi_id = generate_uuid()
    li_id = generate_uuid()
    session.add_all(
        [
            Carrera(id=tpi_id, nombre="TPI", codigo="TPI"),
            Carrera(id=li_id, nombre="LI", codigo="LI"),
        ]
    )
    session.add_all(
        [
            PlanDeEstudio(id=generate_uuid(), carrera_id=tpi_id, nombre="Plan TPI 2015", anio=2015),
            PlanDeEstudio(id=generate_uuid(), carrera_id=tpi_id, nombre="Plan TPI 2018", anio=2018),
            PlanDeEstudio(id=generate_uuid(), carrera_id=tpi_id, nombre="Plan TPI 2020", anio=2020),
            PlanDeEstudio(id=generate_uuid(), carrera_id=tpi_id, nombre="Plan TPI 2021", anio=2021),
            PlanDeEstudio(id=generate_uuid(), carrera_id=li_id, nombre="Plan LI 2018", anio=2018),
            PlanDeEstudio(id=generate_uuid(), carrera_id=li_id, nombre="Plan LI 2020", anio=2020),
            PlanDeEstudio(id=generate_uuid(), carrera_id=li_id, nombre="Plan LI 2021", anio=2021),
        ]
    )
    for codigo in ["80005", "80010", "80015", "80020", "80025", "80030", "80035"]:
        session.add(Materia(id=generate_uuid(), nombre=codigo, codigo=codigo))
    await session.commit()


@pytest.mark.asyncio
async def test_import_students_from_csv(db_session: AsyncSession) -> None:
    await _seed(db_session)
    service = GuaraniImporterService(db_session)

    upserted, skipped = await service.import_students(SAMPLE_DATA / "datos_personales.csv")

    alumnos = (await db_session.execute(select(Alumno))).scalars().all()
    assert upserted > 0
    assert skipped == 0
    assert len(alumnos) == upserted


@pytest.mark.asyncio
async def test_import_enrollment_history_from_csv(db_session: AsyncSession) -> None:
    await _seed(db_session)
    service = GuaraniImporterService(db_session)
    await service.import_students(SAMPLE_DATA / "datos_personales.csv")

    upserted, skipped = await service.import_enrollment_history(SAMPLE_DATA / "alumnos_guarani.csv")

    cursadas = (await db_session.execute(select(Cursada))).scalars().all()
    assert upserted > 0
    assert skipped == 0
    assert len(cursadas) == upserted


@pytest.mark.asyncio
async def test_import_enrollments_from_csv(db_session: AsyncSession) -> None:
    await _seed(db_session)
    service = GuaraniImporterService(db_session)
    await service.import_students(SAMPLE_DATA / "datos_personales.csv")

    upserted, skipped = await service.import_enrollments(SAMPLE_DATA / "inscripciones.csv")

    cursadas = (await db_session.execute(select(Cursada))).scalars().all()
    assert upserted > 0
    assert skipped == 0
    assert len(cursadas) == upserted
