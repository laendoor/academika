import logging
import uuid
from pathlib import Path
from typing import Self

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import generate_uuid
from app.db.session import SessionDep
from app.importers.guarani.parsers import (
    parse_courses,
    parse_degrees,
    parse_enrollment_history,
    parse_enrollments,
    parse_prerequisites,
    parse_students,
    parse_study_plan_courses,
)
from app.importers.guarani.types import (
    CourseRow,
    DegreeRow,
    EnrollmentHistoryRow,
    EnrollmentRow,
    PrerequisiteRow,
    StudentRow,
    StudyPlanCourseRow,
)
from app.importers.utils import date_to_year_term
from app.models.course import Course
from app.models.course_enrollment import CourseEnrollment
from app.models.course_prerequisite import CoursePrerequisite
from app.models.degree import Degree
from app.models.student import Student
from app.models.study_plan import StudyPlan, study_plan_course

logger = logging.getLogger(__name__)

_RESULT_TO_STATUS: dict[str, str] = {
    "I": "inscripto",
    "P": "promocionado",
    "A": "aprobado",
    "D": "desaprobado",
    "R": "regular",
    "PA": "pendiente_aprobacion",
}


def _result_to_status(result: str) -> str:
    code = result.strip().upper()
    return _RESULT_TO_STATUS.get(code, "__unknown__")


class GuaraniImporterService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @classmethod
    def dep(cls, session: SessionDep) -> Self:
        return cls(session)

    async def import_degrees(self, path: Path) -> tuple[int, int]:
        rows = parse_degrees(path)
        return await self._upsert_degrees(rows)

    async def import_courses(self, path: Path) -> tuple[int, int]:
        rows = parse_courses(path)
        return await self._upsert_courses(rows)

    async def import_study_plans(self, paths: list[Path]) -> tuple[int, int]:
        rows: list[StudyPlanCourseRow] = []
        for path in paths:
            rows.extend(parse_study_plan_courses(path))
        return await self._upsert_study_plans(rows)

    async def import_prerequisites(self, paths: list[Path]) -> tuple[int, int]:
        rows: list[PrerequisiteRow] = []
        for path in paths:
            rows.extend(parse_prerequisites(path))
        return await self._upsert_prerequisites(rows)

    async def import_students(self, path: Path) -> tuple[int, int]:
        rows = parse_students(path)
        return await self._upsert_students(rows)

    async def import_enrollment_history(self, path: Path) -> tuple[int, int]:
        rows = parse_enrollment_history(path)
        return await self._upsert_enrollment_history(rows)

    async def import_enrollments(self, path: Path) -> tuple[int, int]:
        rows = parse_enrollments(path)
        return await self._upsert_enrollments(rows)

    async def _upsert_students(self, rows: list[StudentRow]) -> tuple[int, int]:
        degrees = await self._fetch_degrees()
        study_plans = await self._fetch_study_plans()

        upserted = 0
        skipped = 0

        for row in rows:
            degree = degrees.get(row.degree_code)
            if degree is None:
                logger.warning(
                    "import_students: degree '%s' not found — skipping doc_id=%s",
                    row.degree_code,
                    row.doc_id,
                )
                skipped += 1
                continue

            plan = study_plans.get((degree.id, row.study_plan_year))

            stmt = (
                insert(Student)
                .values(
                    id=generate_uuid(),
                    doc_id=row.doc_id,
                    unq_id=row.unq_id,
                    first_name=row.first_name,
                    last_name=row.last_name,
                    email=row.email,
                    enrolled_at=row.enrolled_at,
                    degree_id=degree.id,
                    plan_id=plan.id if plan else None,
                    academic_status="alumno_regular",
                )
                .on_conflict_do_update(
                    index_elements=["doc_id"],
                    set_={  # academic_status intentionally absent: preserve manual overrides
                        "unq_id": row.unq_id,
                        "first_name": row.first_name,
                        "last_name": row.last_name,
                        "email": row.email,
                        "enrolled_at": row.enrolled_at,
                        "degree_id": degree.id,
                        "plan_id": plan.id if plan else None,
                        "updated_at": func.now(),
                    },
                )
            )
            await self.session.execute(stmt)
            upserted += 1

        await self.session.commit()
        return upserted, skipped

    async def _upsert_enrollment_history(self, rows: list[EnrollmentHistoryRow]) -> tuple[int, int]:
        students = await self._fetch_students()
        courses = await self._fetch_courses()
        degrees = await self._fetch_degrees()

        upserted = 0
        skipped = 0

        for row in rows:
            student = students.get(row.doc_id)
            course = courses.get(row.course_code)
            degree = degrees.get(row.degree_code)

            if student is None or course is None or degree is None:
                logger.warning(
                    "import_enrollment_history: missing refs — skipping doc_id=%s course=%s degree=%s",
                    row.doc_id,
                    row.course_code,
                    row.degree_code,
                )
                skipped += 1
                continue

            year, term = date_to_year_term(row.enrollment_date)
            status = _result_to_status(row.result)

            stmt = (
                insert(CourseEnrollment)
                .values(
                    id=generate_uuid(),
                    student_id=student.id,
                    course_id=course.id,
                    degree_id=degree.id,
                    year=year,
                    term=term,
                    enrollment_type=row.enrollment_type,
                    enrollment_status=status,
                    grade=row.grade,
                    enrolled_at=row.enrollment_date,
                    is_regular=row.is_regular,
                    approval_type=row.approval_type,
                    credits=row.credits,
                    plan_year=row.plan_year,
                )
                .on_conflict_do_update(
                    constraint="uq_enrollment_student_course_degree_term",
                    set_={
                        "enrollment_status": status,
                        "grade": row.grade,
                        "enrolled_at": row.enrollment_date,
                        "is_regular": row.is_regular,
                        "approval_type": row.approval_type,
                        "credits": row.credits,
                        "plan_year": row.plan_year,
                        "updated_at": func.now(),
                    },
                )
            )
            await self.session.execute(stmt)
            upserted += 1

        await self.session.commit()
        return upserted, skipped

    async def _upsert_enrollments(self, rows: list[EnrollmentRow]) -> tuple[int, int]:
        students = await self._fetch_students()
        courses = await self._fetch_courses()
        degrees = await self._fetch_degrees()

        upserted = 0
        skipped = 0

        for row in rows:
            student = students.get(row.doc_id)
            course = courses.get(row.course_code)
            degree = degrees.get(row.degree_code)

            if student is None or course is None or degree is None:
                logger.warning(
                    "import_enrollments: missing refs — skipping doc_id=%s course=%s degree=%s",
                    row.doc_id,
                    row.course_code,
                    row.degree_code,
                )
                skipped += 1
                continue

            year, term = date_to_year_term(row.enrollment_date)

            stmt = (
                insert(CourseEnrollment)
                .values(
                    id=generate_uuid(),
                    student_id=student.id,
                    course_id=course.id,
                    degree_id=degree.id,
                    year=year,
                    term=term,
                    section=row.section,
                    enrollment_type="regular",
                    enrollment_status="inscripto",
                    enrolled_at=row.enrollment_date,
                )
                .on_conflict_do_update(
                    constraint="uq_enrollment_student_course_degree_term",
                    set_={
                        "section": row.section,
                        "enrolled_at": row.enrollment_date,
                        "updated_at": func.now(),
                    },
                )
            )
            await self.session.execute(stmt)
            upserted += 1

        await self.session.commit()
        return upserted, skipped

    async def _upsert_degrees(self, rows: list[DegreeRow]) -> tuple[int, int]:
        for row in rows:
            stmt = (
                insert(Degree)
                .values(id=generate_uuid(), code=row.code, name=row.name)
                .on_conflict_do_update(
                    index_elements=["code"],
                    set_={"name": row.name, "updated_at": func.now()},
                )
            )
            await self.session.execute(stmt)
        await self.session.commit()
        return len(rows), 0

    async def _upsert_courses(self, rows: list[CourseRow]) -> tuple[int, int]:
        for row in rows:
            stmt = (
                insert(Course)
                .values(id=generate_uuid(), code=row.code, name=row.name, abbreviation=row.abbreviation)
                .on_conflict_do_update(
                    index_elements=["code"],
                    set_={"name": row.name, "abbreviation": row.abbreviation, "updated_at": func.now()},
                )
            )
            await self.session.execute(stmt)
        await self.session.commit()
        return len(rows), 0

    async def _upsert_study_plans(self, rows: list[StudyPlanCourseRow]) -> tuple[int, int]:
        degrees = await self._fetch_degrees()
        courses = await self._fetch_courses()

        seen: set[tuple[str, int]] = set()
        for row in rows:
            degree = degrees.get(row.degree_code)
            if degree is None:
                continue
            key = (row.degree_code, row.plan_year)
            if key in seen:
                continue
            seen.add(key)
            stmt = (
                insert(StudyPlan)
                .values(id=generate_uuid(), degree_id=degree.id, name=f"Plan {row.plan_year}", year=row.plan_year)
                .on_conflict_do_update(
                    constraint="uq_study_plan_degree_year",
                    set_={"updated_at": func.now()},
                )
            )
            await self.session.execute(stmt)
        await self.session.flush()

        plans = await self._fetch_study_plans()
        upserted = 0
        skipped = 0

        for row in rows:
            degree = degrees.get(row.degree_code)
            course = courses.get(row.course_code)
            if degree is None or course is None:
                logger.warning(
                    "import_study_plans: missing refs — skipping degree=%s course=%s",
                    row.degree_code,
                    row.course_code,
                )
                skipped += 1
                continue
            plan = plans.get((degree.id, row.plan_year))
            if plan is None:
                logger.warning(
                    "import_study_plans: plan not found after upsert — degree=%s year=%d",
                    row.degree_code,
                    row.plan_year,
                )
                skipped += 1
                continue
            link_stmt = insert(study_plan_course).values(plan_id=plan.id, course_id=course.id).on_conflict_do_nothing()
            await self.session.execute(link_stmt)
            upserted += 1

        await self.session.commit()
        return upserted, skipped

    async def _upsert_prerequisites(self, rows: list[PrerequisiteRow]) -> tuple[int, int]:
        degrees = await self._fetch_degrees()
        courses = await self._fetch_courses()
        plans = await self._fetch_study_plans()

        upserted = 0
        skipped = 0

        for row in rows:
            degree = degrees.get(row.degree_code)
            course = courses.get(row.course_code)
            if degree is None or course is None:
                logger.warning(
                    "import_prerequisites: missing refs — skipping degree=%s course=%s",
                    row.degree_code,
                    row.course_code,
                )
                skipped += 1
                continue
            plan = plans.get((degree.id, row.plan_year))
            if plan is None:
                logger.warning(
                    "import_prerequisites: plan not found — degree=%s year=%d",
                    row.degree_code,
                    row.plan_year,
                )
                skipped += 1
                continue

            # required_codes overwrite recommended_codes when a code appears in both
            prereqs: dict[str, bool] = {code: False for code in row.recommended_codes}
            prereqs.update({code: True for code in row.required_codes})
            for prereq_code, is_required in prereqs.items():
                prereq = courses.get(prereq_code)
                if prereq is None:
                    logger.warning("import_prerequisites: prerequisite course not found — code=%s", prereq_code)
                    skipped += 1
                    continue
                stmt = (
                    insert(CoursePrerequisite)
                    .values(
                        plan_id=plan.id,
                        course_id=course.id,
                        prerequisite_id=prereq.id,
                        is_required=is_required,
                    )
                    .on_conflict_do_update(
                        index_elements=["plan_id", "course_id", "prerequisite_id"],
                        set_={"is_required": is_required, "updated_at": func.now()},
                    )
                )
                await self.session.execute(stmt)
                upserted += 1

        await self.session.commit()
        return upserted, skipped

    async def _fetch_degrees(self) -> dict[str, Degree]:
        result = await self.session.execute(select(Degree))
        return {d.code: d for d in result.scalars().all()}

    async def _fetch_study_plans(self) -> dict[tuple[uuid.UUID, int], StudyPlan]:
        result = await self.session.execute(select(StudyPlan))
        return {(sp.degree_id, sp.year): sp for sp in result.scalars().all()}

    async def _fetch_students(self) -> dict[str, Student]:
        result = await self.session.execute(select(Student))
        return {s.doc_id: s for s in result.scalars().all()}

    async def _fetch_courses(self) -> dict[str, Course]:
        result = await self.session.execute(select(Course))
        return {c.code: c for c in result.scalars().all()}
