import uuid
from datetime import date
from unittest.mock import MagicMock

from app.importers.guarani.types import StudentRow


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
