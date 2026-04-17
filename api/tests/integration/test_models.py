import pytest
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.alumno import Alumno
from app.models.carrera import Carrera
from app.models.cursada import Cursada
from app.models.inscripcion import Inscripcion
from app.models.materia import Materia
from app.models.plan_de_estudio import PlanDeEstudio, plan_materia


@pytest.mark.asyncio
async def test_crear_carrera(db_session: AsyncSession) -> None:
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
async def test_plan_de_estudio_vinculado_a_carrera(db_session: AsyncSession) -> None:
    carrera = Carrera(nombre="Licenciatura en Informática", codigo="LI")
    db_session.add(carrera)
    await db_session.commit()

    plan = PlanDeEstudio(carrera_id=carrera.id, nombre="Plan 2015", anio=2015)
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)

    assert plan.carrera_id == carrera.id
    assert plan.activo is True


@pytest.mark.asyncio
async def test_materia_asociada_a_plan(db_session: AsyncSession) -> None:
    carrera = Carrera(nombre="Tecnicatura en Programación Informática", codigo="TPI2")
    db_session.add(carrera)
    await db_session.commit()

    plan = PlanDeEstudio(carrera_id=carrera.id, nombre="Plan 2018", anio=2018)
    materia = Materia(nombre="Introducción a la Programación", codigo="IP", siglas="IP")
    db_session.add_all([plan, materia])
    await db_session.commit()

    # En async SQLAlchemy los lazy loads sincrónicos no funcionan —
    # insertar en la association table directamente y verificar con selectinload.
    await db_session.execute(insert(plan_materia).values(plan_id=plan.id, materia_id=materia.id))
    await db_session.commit()

    result = await db_session.execute(
        select(PlanDeEstudio).options(selectinload(PlanDeEstudio.materias)).where(PlanDeEstudio.id == plan.id)
    )
    loaded_plan = result.scalar_one()
    assert len(loaded_plan.materias) == 1
    assert loaded_plan.materias[0].codigo == "IP"


@pytest.mark.asyncio
async def test_crear_alumno(db_session: AsyncSession) -> None:
    carrera = Carrera(nombre="Licenciatura en Informática", codigo="LI2")
    db_session.add(carrera)
    await db_session.commit()

    alumno = Alumno(
        legajo="12345",
        nombre="Ana",
        apellido="Pérez",
        dni="30123456",
        carrera_id=carrera.id,
        es_regular=True,
    )
    db_session.add(alumno)
    await db_session.commit()
    await db_session.refresh(alumno)

    assert alumno.id is not None
    assert alumno.legajo == "12345"
    assert alumno.plan_id is None


@pytest.mark.asyncio
async def test_crear_cursada(db_session: AsyncSession) -> None:
    carrera = Carrera(nombre="Tecnicatura en Programación Informática", codigo="TPI3")
    materia = Materia(nombre="Algoritmos", codigo="ALG")
    db_session.add_all([carrera, materia])
    await db_session.commit()

    alumno = Alumno(legajo="22222", nombre="Bruno", apellido="López", dni="31111111", carrera_id=carrera.id)
    db_session.add(alumno)
    await db_session.commit()

    cursada = Cursada(
        alumno_id=alumno.id,
        materia_id=materia.id,
        periodo="1C",
        anio=2024,
        resultado="A",
        nota="8",
    )
    db_session.add(cursada)
    await db_session.commit()
    await db_session.refresh(cursada)

    assert cursada.id is not None
    assert cursada.resultado == "A"


@pytest.mark.asyncio
async def test_crear_inscripcion(db_session: AsyncSession) -> None:
    carrera = Carrera(nombre="Licenciatura en Informática", codigo="LI3")
    materia = Materia(nombre="Bases de Datos", codigo="BD")
    db_session.add_all([carrera, materia])
    await db_session.commit()

    alumno = Alumno(legajo="33333", nombre="Carla", apellido="Gómez", dni="32222222", carrera_id=carrera.id)
    db_session.add(alumno)
    await db_session.commit()

    inscripcion = Inscripcion(
        alumno_id=alumno.id,
        materia_id=materia.id,
        periodo="2C",
        anio=2025,
        comision="A",
    )
    db_session.add(inscripcion)
    await db_session.commit()
    await db_session.refresh(inscripcion)

    assert inscripcion.id is not None
    assert inscripcion.comision == "A"
