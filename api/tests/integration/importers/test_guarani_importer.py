from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import generate_uuid
from app.models.course import Course
from app.models.course_enrollment import CourseEnrollment
from app.models.course_prerequisite import CoursePrerequisite
from app.models.degree import Degree
from app.models.student import Student
from app.models.study_plan import StudyPlan
from app.models.study_plans_courses import study_plans_courses
from app.services.guarani_importer import GuaraniImporterService

SAMPLE_DATA = Path(__file__).parents[3] / "sample-data"


async def _seed(session: AsyncSession) -> None:
    tpi_id = generate_uuid()
    li_id = generate_uuid()
    session.add_all(
        [
            Degree(id=tpi_id, name="TPI", code="TPI"),
            Degree(id=li_id, name="LI", code="LI"),
        ]
    )
    session.add_all(
        [
            StudyPlan(id=generate_uuid(), degree_id=tpi_id, name="Plan TPI 2015", year=2015),
            StudyPlan(id=generate_uuid(), degree_id=tpi_id, name="Plan TPI 2018", year=2018),
            StudyPlan(id=generate_uuid(), degree_id=li_id, name="Plan LI 2018", year=2018),
        ]
    )
    for code in ["80005", "80010", "80015", "80020", "80025", "80030", "80035"]:
        session.add(Course(id=generate_uuid(), name=code, code=code))
    await session.commit()


@pytest.mark.asyncio
async def test_import_students_from_csv(db_session: AsyncSession) -> None:
    await _seed(db_session)
    service = GuaraniImporterService(db_session)

    upserted, skipped = await service.import_students(SAMPLE_DATA / "datos_personales.csv")

    students = (await db_session.execute(select(Student))).scalars().all()
    assert upserted > 0
    assert skipped == 0
    assert len(students) == upserted


@pytest.mark.asyncio
async def test_import_enrollment_history_from_csv(db_session: AsyncSession) -> None:
    await _seed(db_session)
    service = GuaraniImporterService(db_session)
    await service.import_students(SAMPLE_DATA / "datos_personales.csv")

    upserted, skipped = await service.import_enrollment_history(SAMPLE_DATA / "alumnos_guarani.csv")

    enrollments = (await db_session.execute(select(CourseEnrollment))).scalars().all()
    assert upserted > 0
    assert skipped == 0
    assert len(enrollments) == upserted


@pytest.mark.asyncio
async def test_import_enrollments_from_csv(db_session: AsyncSession) -> None:
    await _seed(db_session)
    service = GuaraniImporterService(db_session)
    await service.import_students(SAMPLE_DATA / "datos_personales.csv")

    upserted, skipped = await service.import_enrollments(SAMPLE_DATA / "inscripciones.csv")

    enrollments = (await db_session.execute(select(CourseEnrollment))).scalars().all()
    assert upserted > 0
    assert skipped == 0
    assert len(enrollments) == upserted


@pytest.mark.asyncio
async def test_idempotency_students(db_session: AsyncSession) -> None:
    await _seed(db_session)
    service = GuaraniImporterService(db_session)
    path = SAMPLE_DATA / "datos_personales.csv"

    upserted_1, _ = await service.import_students(path)
    upserted_2, _ = await service.import_students(path)

    students = (await db_session.execute(select(Student))).scalars().all()
    assert upserted_1 == upserted_2
    assert len(students) == upserted_1


@pytest.mark.asyncio
async def test_idempotency_enrollment_history(db_session: AsyncSession) -> None:
    await _seed(db_session)
    service = GuaraniImporterService(db_session)
    await service.import_students(SAMPLE_DATA / "datos_personales.csv")
    path = SAMPLE_DATA / "alumnos_guarani.csv"

    upserted_1, _ = await service.import_enrollment_history(path)
    upserted_2, _ = await service.import_enrollment_history(path)

    enrollments = (await db_session.execute(select(CourseEnrollment))).scalars().all()
    assert upserted_1 == upserted_2
    assert len(enrollments) == upserted_1


@pytest.mark.asyncio
async def test_idempotency_enrollments(db_session: AsyncSession) -> None:
    await _seed(db_session)
    service = GuaraniImporterService(db_session)
    await service.import_students(SAMPLE_DATA / "datos_personales.csv")
    path = SAMPLE_DATA / "inscripciones.csv"

    upserted_1, _ = await service.import_enrollments(path)
    upserted_2, _ = await service.import_enrollments(path)

    enrollments = (await db_session.execute(select(CourseEnrollment))).scalars().all()
    assert upserted_1 == upserted_2
    assert len(enrollments) == upserted_1


@pytest.mark.asyncio
async def test_reimport_preserves_manual_academic_status(db_session: AsyncSession) -> None:
    await _seed(db_session)
    service = GuaraniImporterService(db_session)
    await service.import_students(SAMPLE_DATA / "datos_personales.csv")

    student = (await db_session.execute(select(Student))).scalars().first()
    assert student is not None
    student.academic_status = "no_regular"
    await db_session.commit()

    await service.import_students(SAMPLE_DATA / "datos_personales.csv")

    await db_session.refresh(student)
    assert student.academic_status == "no_regular"


@pytest.mark.asyncio
async def test_skips_missing_degree(db_session: AsyncSession) -> None:
    service = GuaraniImporterService(db_session)

    upserted, skipped = await service.import_students(SAMPLE_DATA / "datos_personales.csv")

    students = (await db_session.execute(select(Student))).scalars().all()
    assert upserted == 0
    assert skipped > 0
    assert len(students) == 0


# ---------------------------------------------------------------------------
# Degrees
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_import_degrees_from_csv(db_session: AsyncSession) -> None:
    service = GuaraniImporterService(db_session)

    upserted, skipped = await service.import_degrees(SAMPLE_DATA / "carreras.csv")

    degrees = (await db_session.execute(select(Degree))).scalars().all()
    assert upserted > 0
    assert skipped == 0
    assert len(degrees) == upserted


@pytest.mark.asyncio
async def test_idempotency_degrees(db_session: AsyncSession) -> None:
    service = GuaraniImporterService(db_session)
    path = SAMPLE_DATA / "carreras.csv"

    upserted_1, _ = await service.import_degrees(path)
    upserted_2, _ = await service.import_degrees(path)

    degrees = (await db_session.execute(select(Degree))).scalars().all()
    assert upserted_1 == upserted_2
    assert len(degrees) == upserted_1


# ---------------------------------------------------------------------------
# Courses
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_import_courses_from_csv(db_session: AsyncSession) -> None:
    service = GuaraniImporterService(db_session)

    upserted, skipped = await service.import_courses(SAMPLE_DATA / "materias.csv")

    courses = (await db_session.execute(select(Course))).scalars().all()
    assert upserted > 0
    assert skipped == 0
    # The same course code can appear in multiple plan rows; upsert deduplicates by code
    assert len(courses) <= upserted
    assert len(courses) > 0


@pytest.mark.asyncio
async def test_idempotency_courses(db_session: AsyncSession) -> None:
    service = GuaraniImporterService(db_session)
    path = SAMPLE_DATA / "materias.csv"

    upserted_1, _ = await service.import_courses(path)
    upserted_2, _ = await service.import_courses(path)

    courses = (await db_session.execute(select(Course))).scalars().all()
    assert upserted_1 == upserted_2
    assert len(courses) > 0


# ---------------------------------------------------------------------------
# Study plans
# ---------------------------------------------------------------------------


async def _seed_degrees_and_courses(session: AsyncSession) -> None:
    service = GuaraniImporterService(session)
    await service.import_degrees(SAMPLE_DATA / "carreras.csv")
    await service.import_courses(SAMPLE_DATA / "materias.csv")


@pytest.mark.asyncio
async def test_import_study_plans_from_csv(db_session: AsyncSession) -> None:
    await _seed_degrees_and_courses(db_session)
    service = GuaraniImporterService(db_session)
    paths = [SAMPLE_DATA / "planes_tpi.csv", SAMPLE_DATA / "planes_lds.csv"]

    upserted, skipped = await service.import_study_plans(paths)

    plans = (await db_session.execute(select(StudyPlan))).scalars().all()
    links = (await db_session.execute(select(study_plans_courses))).all()
    assert upserted > 0
    # Real data may reference courses not present in materias.csv — skips are expected
    assert skipped >= 0
    assert len(plans) > 0
    assert len(links) == upserted


@pytest.mark.asyncio
async def test_idempotency_study_plans(db_session: AsyncSession) -> None:
    await _seed_degrees_and_courses(db_session)
    service = GuaraniImporterService(db_session)
    paths = [SAMPLE_DATA / "planes_tpi.csv", SAMPLE_DATA / "planes_lds.csv"]

    upserted_1, _ = await service.import_study_plans(paths)
    upserted_2, _ = await service.import_study_plans(paths)

    links = (await db_session.execute(select(study_plans_courses))).all()
    assert upserted_1 == upserted_2
    assert len(links) == upserted_1


# ---------------------------------------------------------------------------
# Prerequisites
# ---------------------------------------------------------------------------


async def _seed_full(session: AsyncSession) -> None:
    await _seed_degrees_and_courses(session)
    service = GuaraniImporterService(session)
    await service.import_study_plans([SAMPLE_DATA / "planes_tpi.csv", SAMPLE_DATA / "planes_lds.csv"])


@pytest.mark.asyncio
async def test_import_prerequisites_from_csv(db_session: AsyncSession) -> None:
    await _seed_full(db_session)
    service = GuaraniImporterService(db_session)
    paths = [SAMPLE_DATA / "requisitos_tpi.csv", SAMPLE_DATA / "requisitos_lds.csv"]

    upserted, skipped = await service.import_prerequisites(paths)

    prereqs = (await db_session.execute(select(CoursePrerequisite))).scalars().all()
    assert upserted > 0
    # Real data may reference courses/plans not fully covered by the seeded data
    assert skipped >= 0
    assert len(prereqs) == upserted


@pytest.mark.asyncio
async def test_idempotency_prerequisites(db_session: AsyncSession) -> None:
    await _seed_full(db_session)
    service = GuaraniImporterService(db_session)
    paths = [SAMPLE_DATA / "requisitos_tpi.csv", SAMPLE_DATA / "requisitos_lds.csv"]

    upserted_1, _ = await service.import_prerequisites(paths)
    upserted_2, _ = await service.import_prerequisites(paths)

    prereqs = (await db_session.execute(select(CoursePrerequisite))).scalars().all()
    assert upserted_1 == upserted_2
    assert len(prereqs) == upserted_1
