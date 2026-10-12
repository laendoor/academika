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


def _read(name: str) -> str:
    return (SAMPLE_DATA / name).read_text(encoding="utf-8")


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
async def test_importar_alumnos_desde_csv(db_session: AsyncSession) -> None:
    await _seed(db_session)
    service = GuaraniImporterService(db_session)

    upserted, skipped = await service.importar_alumnos([_read("datos_personales.csv")])

    alumnos = (await db_session.execute(select(Alumno))).scalars().all()
    assert upserted > 0
    assert skipped == 0
    assert len(alumnos) == upserted


@pytest.mark.asyncio
async def test_importar_historial_cursadas_desde_csv(db_session: AsyncSession) -> None:
    await _seed(db_session)
    service = GuaraniImporterService(db_session)
    await service.importar_alumnos([_read("datos_personales.csv")])

    upserted, skipped = await service.importar_historial_cursadas([_read("alumnos_guarani.csv")])

    cursadas = (await db_session.execute(select(Cursada))).scalars().all()
    assert upserted > 0
    assert skipped == 0
    assert len(cursadas) == upserted


@pytest.mark.asyncio
async def test_importar_inscripciones_desde_csv(db_session: AsyncSession) -> None:
    await _seed(db_session)
    service = GuaraniImporterService(db_session)
    await service.importar_alumnos([_read("datos_personales.csv")])

    upserted, skipped = await service.importar_inscripciones([_read("inscripciones.csv")])

    cursadas = (await db_session.execute(select(Cursada))).scalars().all()
    assert upserted > 0
    assert skipped == 0
    assert len(cursadas) == upserted


PLANES_CSV = """Codigo Carrera;Plan;Cuatrimestre;Nucleo;Area;Codigo;Creditos;Nombre
TPI;2015;1;Básico;Programación;80005;8;Elementos de Programación
TPI;2015;1;A;Matemática;80010;6;Algoritmos
"""


@pytest.mark.asyncio
async def test_importar_planes_actualiza_materia(db_session: AsyncSession) -> None:
    await _seed(db_session)
    service = GuaraniImporterService(db_session)

    upserted, skipped = await service.importar_planes([PLANES_CSV])

    assert skipped == 0
    assert upserted == 2
    materia = (await db_session.execute(select(Materia).where(Materia.codigo == "80005"))).scalars().one()
    assert materia.nucleo == "basico"
    assert materia.creditos == 8
    # código de núcleo desconocido ("A" en exports reales) → warn + null, pero los créditos se guardan
    materia_a = (await db_session.execute(select(Materia).where(Materia.codigo == "80010"))).scalars().one()
    assert materia_a.nucleo is None
    assert materia_a.creditos == 6


HISTORIAL_SIN_CREDITOS = (
    "Legajo;DNI;Carrera;Regular;Calidad;Cod.Materia;Nombre_materia;Fecha;Result;Nota;"
    "Forma Aprobación;Créditos;Acta Promo;Acta Ex;Plan\n"
    "12001;35120001;TPI;;;80005;Elementos de Programación;01/07/2018;P;9;Promoción;;;1001;2015\n"
)


@pytest.mark.asyncio
async def test_historial_preserva_creditos_en_reimport_sin_dato(db_session: AsyncSession) -> None:
    await _seed(db_session)
    service = GuaraniImporterService(db_session)
    await service.importar_alumnos([_read("datos_personales.csv")])
    await service.importar_historial_cursadas([_read("alumnos_guarani.csv")])

    upserted, skipped = await service.importar_historial_cursadas([HISTORIAL_SIN_CREDITOS])

    assert skipped == 0
    assert upserted == 1
    alumno_id = (await db_session.execute(select(Alumno.id).where(Alumno.dni == "35120001"))).scalar_one()
    materia_id = (await db_session.execute(select(Materia.id).where(Materia.codigo == "80005"))).scalar_one()
    cursada = (
        (
            await db_session.execute(
                select(Cursada).where(Cursada.alumno_id == alumno_id, Cursada.materia_id == materia_id)
            )
        )
        .scalars()
        .one()
    )
    assert cursada.creditos == 10
