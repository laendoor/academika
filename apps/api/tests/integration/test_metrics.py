from pathlib import Path

import pytest
from analytika import find_metric
from analytika.errors import MetricaNotFoundError, MetricaParamError
from db.base import generate_uuid
from db.models.alumno import Alumno
from db.models.alumno_carrera import AlumnoCarrera
from db.models.carrera import Carrera
from db.models.materia import Materia
from db.models.plan_de_estudio import PlanDeEstudio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.importers.guarani.parsers import parse_courses, parse_study_plan_courses
from app.services.guarani_importer import GuaraniImporterService

DATA = Path(__file__).parents[4] / "datos-prueba"


def _read(name: str) -> str:
    return (DATA / name).read_text(encoding="utf-8")


async def _seed(session: AsyncSession) -> None:
    service = GuaraniImporterService(session)
    await service.importar_carreras([_read("carreras.csv")])
    await service.importar_materias([_read("materias.csv")])

    # materias.csv no cubre todos los códigos que listan los planes: el import de
    # planes los saltearía y el total de avance daría 47 en vez de 52.
    existentes = {row.code for row in parse_courses(_read("materias.csv"))}
    codigos = {
        row.course_code
        for name in ("planes_tpi.csv", "planes_lds.csv")
        for row in parse_study_plan_courses(_read(name))
    }
    for code in sorted(codigos - existentes):
        session.add(Materia(id=generate_uuid(), codigo=code, nombre=code))
    await session.commit()

    await service.importar_planes([_read("planes_tpi.csv"), _read("planes_lds.csv")])
    await service.importar_alumnos([_read("datos_personales.csv")])
    _, skipped = await service.importar_historial_cursadas([_read("alumnos_guarani.csv")])
    assert skipped == 0


async def _run(session: AsyncSession, key: str, **params: str) -> list[dict]:
    metrica = find_metric(key)
    assert metrica is not None
    return await metrica.run(session, params)


async def test_historia(db_session: AsyncSession) -> None:
    await _seed(db_session)

    rows = await _run(db_session, "historia", alu="35120001")
    assert len(rows) == 21
    assert all(set(row) == {"carrera", "cod_mat", "materia", "nota", "estado", "fecha"} for row in rows)
    assert [row["fecha"] for row in rows] == sorted(row["fecha"] for row in rows)
    aplazos = [(row["cod_mat"], row["nota"]) for row in rows if row["estado"] == "desaprobado"]
    assert aplazos == [("1042", "2")]

    dos_carreras = await _run(db_session, "historia", alu="37450023")
    assert len(dos_carreras) == 46
    assert [row["carrera"] for row in dos_carreras] == sorted(row["carrera"] for row in dos_carreras)

    assert await _run(db_session, "historia", alu="45999011") == []

    with pytest.raises(MetricaNotFoundError, match="no encontrado"):
        await _run(db_session, "historia", alu="00000000")


async def test_promedios(db_session: AsyncSession) -> None:
    await _seed(db_session)

    [general] = await _run(db_session, "promedios")
    assert general == {"general": 6.97, "general_sin_aplazos": 7.5, "reciente": 7.05, "reciente_sin_aplazos": 7.34}

    [un_alumno] = await _run(db_session, "promedios", ingreso="2018")
    assert un_alumno == {"general": 7.24, "general_sin_aplazos": 7.5, "reciente": 6.86, "reciente_sin_aplazos": 7.67}

    [por_plan] = await _run(db_session, "promedios", plan="2019")
    assert (por_plan["general"], por_plan["general_sin_aplazos"]) == (6.89, 7.28)

    [sin_cohorte] = await _run(db_session, "promedios", estado="no_regular")
    assert sin_cohorte == {"general": None, "general_sin_aplazos": None, "reciente": None, "reciente_sin_aplazos": None}

    with pytest.raises(MetricaParamError, match="ingreso"):
        await _run(db_session, "promedios", ingreso="abc")


async def test_avance(db_session: AsyncSession) -> None:
    await _seed(db_session)

    [total] = await _run(db_session, "avance", alu="35120001")
    assert total == {"carrera": "P", "corte": "total", "aprobadas": 20, "total": 52, "porcentaje": 38.5}

    filas = await _run(db_session, "avance", alu="35120001", group_by="area")
    cortes = [fila for fila in filas if fila["corte"] != "total"]
    assert sum(fila["total"] for fila in cortes) == 52
    assert sum(fila["aprobadas"] for fila in cortes) == 20
    assert any(fila["corte"] == "area: sin area" for fila in filas)
    assert await _run(db_session, "avance", alu="35120001", group_by="area,area") == filas

    dos_carreras = await _run(db_session, "avance", alu="37450023")
    assert [(fila["carrera"], fila["aprobadas"], fila["total"]) for fila in dos_carreras] == [
        ("P", 17, 52),
        ("W", 21, 57),
    ]

    [sin_datos] = await _run(db_session, "avance", alu="45999011")
    assert (sin_datos["aprobadas"], sin_datos["porcentaje"]) == (0, 0.0)

    with pytest.raises(MetricaParamError, match="group_by"):
        await _run(db_session, "avance", alu="35120001", group_by="plan")


async def test_avance_usa_plan_vigente(db_session: AsyncSession) -> None:
    await _seed(db_session)

    plan_viejo = (
        (
            await db_session.execute(
                select(PlanDeEstudio)
                .join(Carrera, PlanDeEstudio.carrera_id == Carrera.id)
                .where(Carrera.codigo == "P", PlanDeEstudio.anio == 2007)
            )
        )
        .scalars()
        .one()
    )
    alumno = (await db_session.execute(select(Alumno).where(Alumno.dni == "35120001"))).scalars().one()
    db_session.add(AlumnoCarrera(alumno_id=alumno.id, plan_id=plan_viejo.id, estado_academico="alumno_regular"))
    await db_session.commit()

    filas = await _run(db_session, "avance", alu="35120001")
    assert [(fila["carrera"], fila["total"]) for fila in filas] == [("P", 52)]
