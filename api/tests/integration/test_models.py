import pytest
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.alumno import Alumno
from app.models.alumno_carrera import AlumnoCarrera
from app.models.carrera import Carrera
from app.models.cursada import Cursada
from app.models.materia import Materia
from app.models.plan_de_estudio import PlanDeEstudio
from app.models.planes_materias import planes_materias


@pytest.mark.asyncio
async def test_create_carrera(db_session: AsyncSession) -> None:
    carrera = Carrera(nombre="Tecnicatura en Programación Informática", codigo="TPI")
    db_session.add(carrera)
    await db_session.commit()
    await db_session.refresh(carrera)

    result = await db_session.execute(select(Carrera).where(Carrera.codigo == "TPI"))
    found = result.scalar_one()
    assert found.nombre == "Tecnicatura en Programación Informática"
    assert found.id is not None
    assert found.created_at is not None


@pytest.mark.asyncio
async def test_plan_linked_to_carrera(db_session: AsyncSession) -> None:
    carrera = Carrera(nombre="Licenciatura en Informática", codigo="LI")
    db_session.add(carrera)
    await db_session.commit()

    plan = PlanDeEstudio(carrera_id=carrera.id, nombre="Plan 2015", anio=2015)
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)

    assert plan.carrera_id == carrera.id
    assert plan.vigente is True


@pytest.mark.asyncio
async def test_materia_linked_to_plan(db_session: AsyncSession) -> None:
    carrera = Carrera(nombre="Tecnicatura en Programación Informática", codigo="TPI2")
    db_session.add(carrera)
    await db_session.commit()

    plan = PlanDeEstudio(carrera_id=carrera.id, nombre="Plan 2018", anio=2018)
    materia = Materia(nombre="Introducción a la Programación", codigo="IP", sigla="IP")
    db_session.add_all([plan, materia])
    await db_session.commit()

    # En async SQLAlchemy los lazy loads sincrónicos no funcionan —
    # insertar en la association table directamente y verificar con selectinload.
    await db_session.execute(insert(planes_materias).values(plan_id=plan.id, materia_id=materia.id))
    await db_session.commit()

    result = await db_session.execute(
        select(PlanDeEstudio).options(selectinload(PlanDeEstudio.materias)).where(PlanDeEstudio.id == plan.id)
    )
    loaded_plan = result.scalar_one()
    assert len(loaded_plan.materias) == 1
    assert loaded_plan.materias[0].codigo == "IP"


@pytest.mark.asyncio
async def test_create_alumno(db_session: AsyncSession) -> None:
    carrera = Carrera(nombre="Licenciatura en Informática", codigo="LI2")
    db_session.add(carrera)
    await db_session.commit()

    plan = PlanDeEstudio(carrera_id=carrera.id, nombre="Plan 2020", anio=2020)
    db_session.add(plan)
    await db_session.commit()

    alumno = Alumno(nombre="Ana", apellido="Pérez", dni="30123456")
    db_session.add(alumno)
    await db_session.commit()

    inscripcion = AlumnoCarrera(alumno_id=alumno.id, plan_id=plan.id, estado_academico="alumno_regular")
    db_session.add(inscripcion)
    await db_session.commit()
    await db_session.refresh(alumno)

    assert alumno.id is not None
    assert alumno.dni == "30123456"
    assert inscripcion.estado_academico == "alumno_regular"


@pytest.mark.asyncio
async def test_create_cursada(db_session: AsyncSession) -> None:
    carrera = Carrera(nombre="Tecnicatura en Programación Informática", codigo="TPI3")
    materia = Materia(nombre="Algoritmos", codigo="ALG")
    db_session.add_all([carrera, materia])
    await db_session.commit()

    alumno = Alumno(nombre="Bruno", apellido="López", dni="31111111")
    db_session.add(alumno)
    await db_session.commit()

    cursada = Cursada(
        alumno_id=alumno.id,
        materia_id=materia.id,
        carrera_id=carrera.id,
        anio=2024,
        cuatrimestre="1C",
        tipo_cursada="regular",
        estado_cursada="inscripto",
    )
    db_session.add(cursada)
    await db_session.commit()
    await db_session.refresh(cursada)

    assert cursada.id is not None
    assert cursada.estado_cursada == "inscripto"
    assert cursada.nota is None
    assert cursada.fecha_cambio_estado is None
