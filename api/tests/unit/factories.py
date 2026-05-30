import uuid
from datetime import date
from unittest.mock import MagicMock

from app.importers.guarani.types import (
    CourseRow,
    DegreeRow,
    EnrollmentHistoryRow,
    EnrollmentRow,
    PrerequisiteRow,
    StudentRow,
    StudyPlanCourseRow,
)


def make_degree_row(code: str = "TPI", name: str = "Tecnicatura en Programación") -> DegreeRow:
    return DegreeRow(code=code, name=name)


def make_course_row(code: str = "101", name: str = "Algoritmos", abbreviation: str | None = "algo") -> CourseRow:
    return CourseRow(code=code, name=name, abbreviation=abbreviation)


def make_study_plan_course_row(
    degree_code: str = "TPI",
    plan_year: int = 2015,
    course_code: str = "101",
) -> StudyPlanCourseRow:
    return StudyPlanCourseRow(degree_code=degree_code, plan_year=plan_year, course_code=course_code)


def make_prerequisite_row(
    degree_code: str = "TPI",
    plan_year: int = 2015,
    course_code: str = "102",
    required_codes: list[str] | None = None,
    recommended_codes: list[str] | None = None,
) -> PrerequisiteRow:
    return PrerequisiteRow(
        degree_code=degree_code,
        plan_year=plan_year,
        course_code=course_code,
        required_codes=required_codes if required_codes is not None else ["101"],
        recommended_codes=recommended_codes if recommended_codes is not None else [],
    )


def make_student_row(
    doc_id: str = "12345678",
    degree_code: str = "P",
    plan_year: int = 2015,
) -> StudentRow:
    return StudentRow(
        doc_id=doc_id,
        unq_id="10001",
        first_name="Ana",
        last_name="Pérez",
        email=None,
        degree_code=degree_code,
        study_plan_year=plan_year,
        enrolled_at=date(2018, 3, 1),
    )


def make_degree(code: str = "P") -> MagicMock:
    d = MagicMock()
    d.id = uuid.uuid4()
    d.code = code
    return d


def make_study_plan(degree_id: uuid.UUID, year: int = 2015) -> MagicMock:
    sp = MagicMock()
    sp.id = uuid.uuid4()
    sp.degree_id = degree_id
    sp.year = year
    return sp


def make_student(doc_id: str = "12345678") -> MagicMock:
    s = MagicMock()
    s.id = uuid.uuid4()
    s.doc_id = doc_id
    return s


def make_course(code: str = "ALGO1") -> MagicMock:
    c = MagicMock()
    c.id = uuid.uuid4()
    c.code = code
    return c


def make_enrollment_history_row(
    doc_id: str = "12345678",
    degree_code: str = "P",
    course_code: str = "ALGO1",
    result: str = "A",
) -> EnrollmentHistoryRow:
    return EnrollmentHistoryRow(
        doc_id=doc_id,
        degree_code=degree_code,
        course_code=course_code,
        is_regular="S",
        enrollment_type="regular",
        result=result,
        grade="8",
        approval_type=None,
        credits=6,
        plan_year=2015,
        enrollment_date=date(2024, 7, 1),
    )


def make_enrollment_row(
    doc_id: str = "12345678",
    degree_code: str = "P",
    course_code: str = "ALGO1",
) -> EnrollmentRow:
    return EnrollmentRow(
        doc_id=doc_id,
        degree_code=degree_code,
        course_code=course_code,
        section="K1001",
        enrollment_date=date(2024, 4, 1),
    )
