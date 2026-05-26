import uuid
from datetime import date
from unittest.mock import MagicMock

from app.importers.guarani.types import EnrollmentHistoryRow, EnrollmentRow, StudentRow


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
