from datetime import date

from clika.parser import parse
from clika.repl import execute
from db.base import generate_uuid
from db.models.alumno import Alumno
from db.models.alumno_carrera import AlumnoCarrera
from db.models.carrera import Carrera
from db.models.cursada import Cursada
from db.models.lkp_estado_academico import LkpEstadoAcademico
from db.models.lkp_estado_cursada import LkpEstadoCursada
from db.models.lkp_tipo_cursada import LkpTipoCursada
from db.models.materia import Materia
from db.models.plan_de_estudio import PlanDeEstudio
from db.models.planes_materias import planes_materias
from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as pg_insert


async def _seed(session_factory) -> None:
    async with session_factory() as session:
        await session.execute(pg_insert(LkpEstadoAcademico).values(key="alumno_regular", label="Regular"))
        await session.execute(pg_insert(LkpTipoCursada).values(key="regular", label="Cursada Regular"))
        await session.execute(pg_insert(LkpEstadoCursada).values(key="promocionado", code="P", label="Promocionado"))
        await session.execute(pg_insert(LkpEstadoCursada).values(key="desaprobado", code="D", label="Desaprobado"))

        carrera = Carrera(id=generate_uuid(), codigo="E2E", nombre="Carrera E2E")
        plan = PlanDeEstudio(id=generate_uuid(), carrera_id=carrera.id, nombre="Plan E2E", anio=2020)
        aprobada = Materia(id=generate_uuid(), codigo="E2E-1", nombre="Aprobada", area="Programación")
        pendiente = Materia(id=generate_uuid(), codigo="E2E-2", nombre="Pendiente", area="Matemática")
        alumno = Alumno(id=generate_uuid(), dni="90000001", nombre="Ana", apellido="Test")
        session.add_all([carrera, plan, aprobada, pendiente, alumno])
        await session.flush()

        await session.execute(
            insert(planes_materias).values(
                [{"plan_id": plan.id, "materia_id": aprobada.id}, {"plan_id": plan.id, "materia_id": pendiente.id}]
            )
        )
        session.add_all(
            [
                AlumnoCarrera(
                    alumno_id=alumno.id,
                    plan_id=plan.id,
                    fecha_ingreso=date(2020, 3, 1),
                    estado_academico="alumno_regular",
                ),
                Cursada(
                    id=generate_uuid(),
                    alumno_id=alumno.id,
                    materia_id=aprobada.id,
                    carrera_id=carrera.id,
                    anio=2021,
                    cuatrimestre="1C",
                    tipo_cursada="regular",
                    estado_cursada="promocionado",
                    nota="8",
                    fecha_inscripcion=date(2021, 7, 1),
                ),
                Cursada(
                    id=generate_uuid(),
                    alumno_id=alumno.id,
                    materia_id=pendiente.id,
                    carrera_id=carrera.id,
                    anio=2021,
                    cuatrimestre="2C",
                    tipo_cursada="regular",
                    estado_cursada="desaprobado",
                ),
            ]
        )
        await session.commit()


async def test_metricas_por_clika(session_factory) -> None:
    await _seed(session_factory)

    lista = await execute(parse("metricas"), session_factory)
    for key in ("historia", "promedios", "avance"):
        assert f"| {key}" in lista

    historia = await execute(parse("metrica historia alu=90000001"), session_factory)
    assert historia.splitlines()[0].startswith("| carrera")
    assert len(historia.splitlines()) == 4  # cabecera + regla + dos cursadas
    assert "2021-07-01" in historia
    assert "| -" in historia  # nota y fecha nulas se muestran como guion

    promedios = await execute(parse("metrica promedios"), session_factory)
    assert "| general | general_sin_aplazos | reciente | reciente_sin_aplazos |" in promedios
    assert promedios.count("8.0") == 4

    avance = await execute(parse("metrica avance alu=90000001 group_by=area"), session_factory)
    assert "50.0" in avance
    assert "area: Programación" in avance
    assert "area: Matemática" in avance

    error = await execute(parse("metrica avance"), session_factory)
    assert "falta el parámetro 'alu'" in error
