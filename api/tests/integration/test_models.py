import pytest
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import Course
from app.models.course_enrollment import CourseEnrollment
from app.models.degree import Degree
from app.models.student import Student
from app.models.study_plan import StudyPlan, study_plan_course


@pytest.mark.asyncio
async def test_create_degree(db_session: AsyncSession) -> None:
    degree = Degree(name="Tecnicatura en Programación Informática", code="TPI")
    db_session.add(degree)
    await db_session.commit()
    await db_session.refresh(degree)

    result = await db_session.execute(select(Degree).where(Degree.code == "TPI"))
    found = result.scalar_one()
    assert found.name == "Tecnicatura en Programación Informática"
    assert found.id is not None
    assert found.created_at is not None


@pytest.mark.asyncio
async def test_study_plan_linked_to_degree(db_session: AsyncSession) -> None:
    degree = Degree(name="Licenciatura en Informática", code="LI")
    db_session.add(degree)
    await db_session.commit()

    plan = StudyPlan(degree_id=degree.id, name="Plan 2015", year=2015)
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)

    assert plan.degree_id == degree.id
    assert plan.is_active is True


@pytest.mark.asyncio
async def test_course_linked_to_study_plan(db_session: AsyncSession) -> None:
    degree = Degree(name="Tecnicatura en Programación Informática", code="TPI2")
    db_session.add(degree)
    await db_session.commit()

    plan = StudyPlan(degree_id=degree.id, name="Plan 2018", year=2018)
    course = Course(name="Introducción a la Programación", code="IP", abbreviation="IP")
    db_session.add_all([plan, course])
    await db_session.commit()

    # En async SQLAlchemy los lazy loads sincrónicos no funcionan —
    # insertar en la association table directamente y verificar con selectinload.
    await db_session.execute(insert(study_plan_course).values(plan_id=plan.id, course_id=course.id))
    await db_session.commit()

    result = await db_session.execute(
        select(StudyPlan).options(selectinload(StudyPlan.courses)).where(StudyPlan.id == plan.id)
    )
    loaded_plan = result.scalar_one()
    assert len(loaded_plan.courses) == 1
    assert loaded_plan.courses[0].code == "IP"


@pytest.mark.asyncio
async def test_create_student(db_session: AsyncSession) -> None:
    degree = Degree(name="Licenciatura en Informática", code="LI2")
    db_session.add(degree)
    await db_session.commit()

    student = Student(
        first_name="Ana",
        last_name="Pérez",
        doc_id="30123456",
        degree_id=degree.id,
        academic_status="alumno_regular",
    )
    db_session.add(student)
    await db_session.commit()
    await db_session.refresh(student)

    assert student.id is not None
    assert student.doc_id == "30123456"
    assert student.plan_id is None
    assert student.academic_status == "alumno_regular"


@pytest.mark.asyncio
async def test_create_course_enrollment(db_session: AsyncSession) -> None:
    degree = Degree(name="Tecnicatura en Programación Informática", code="TPI3")
    course = Course(name="Algoritmos", code="ALG")
    db_session.add_all([degree, course])
    await db_session.commit()

    student = Student(
        first_name="Bruno",
        last_name="López",
        doc_id="31111111",
        degree_id=degree.id,
        academic_status="alumno_regular",
    )
    db_session.add(student)
    await db_session.commit()

    enrollment = CourseEnrollment(
        student_id=student.id,
        course_id=course.id,
        degree_id=degree.id,
        year=2024,
        term="1C",
        enrollment_type="regular",
        enrollment_status="inscripto",
    )
    db_session.add(enrollment)
    await db_session.commit()
    await db_session.refresh(enrollment)

    assert enrollment.id is not None
    assert enrollment.enrollment_status == "inscripto"
    assert enrollment.grade is None
    assert enrollment.status_changed_at is None
