from datetime import date
from pathlib import Path

import pytest

from app.importers.guarani.parsers import (
    parse_enrollment_history,
    parse_enrollments,
    parse_students,
)
from app.importers.utils import date_to_year_term

FIXTURES = Path(__file__).parent / "fixtures"


class TestParseDatosPersonales:
    def test_parses_valid_rows(self) -> None:
        rows = parse_students(FIXTURES / "datos_personales.csv")
        assert len(rows) == 2

    def test_fields(self) -> None:
        row = parse_students(FIXTURES / "datos_personales.csv")[0]
        assert row.doc_id == "35120001"
        assert row.unq_id == "12001"
        assert row.first_name == "Martina"
        assert row.last_name == "García"
        assert row.email == "martina.garcia1@hotmail.com"
        assert row.degree_code == "TPI"
        assert row.study_plan_year == 2015
        assert row.enrolled_at == date(2018, 3, 2)

    def test_optional_email_is_none(self) -> None:
        rows = parse_students(FIXTURES / "datos_personales.csv")
        assert rows[1].email is None

    def test_skips_invalid_row(self) -> None:
        rows = parse_students(FIXTURES / "datos_personales.csv")
        assert len(rows) == 2


class TestParseAlumnosGuarani:
    def test_parses_valid_rows(self) -> None:
        rows = parse_enrollment_history(FIXTURES / "alumnos_guarani.csv")
        assert len(rows) == 3

    def test_fields(self) -> None:
        row = parse_enrollment_history(FIXTURES / "alumnos_guarani.csv")[0]
        assert row.doc_id == "35120001"
        assert row.degree_code == "TPI"
        assert row.course_code == "80005"
        assert row.enrollment_type == "regular"
        assert row.result == "P"
        assert row.grade == "4"
        assert row.approval_type == "Examen"
        assert row.credits == 10
        assert row.plan_year == 2015
        assert row.enrollment_date == date(2019, 12, 1)

    def test_calidad_libre(self) -> None:
        rows = parse_enrollment_history(FIXTURES / "alumnos_guarani.csv")
        assert rows[1].enrollment_type == "libre"

    def test_optional_fields_are_none(self) -> None:
        rows = parse_enrollment_history(FIXTURES / "alumnos_guarani.csv")
        assert rows[2].grade is None
        assert rows[2].credits is None
        assert rows[2].plan_year is None

    def test_skips_invalid_row(self) -> None:
        rows = parse_enrollment_history(FIXTURES / "alumnos_guarani.csv")
        assert len(rows) == 3


class TestParseInscripciones:
    def test_parses_valid_rows(self) -> None:
        rows = parse_enrollments(FIXTURES / "inscripciones.csv")
        assert len(rows) == 2

    def test_fields(self) -> None:
        row = parse_enrollments(FIXTURES / "inscripciones.csv")[0]
        assert row.doc_id == "35120001"
        assert row.degree_code == "TPI"
        assert row.course_code == "80005"
        assert row.section == "4"
        assert row.enrollment_date == date(2024, 3, 3)

    def test_optional_section_is_none(self) -> None:
        rows = parse_enrollments(FIXTURES / "inscripciones.csv")
        assert rows[1].section is None


@pytest.mark.parametrize(
    "d,expected",
    [
        (date(2024, 1, 15), (2023, "2C")),
        (date(2024, 2, 28), (2023, "2C")),
        (date(2024, 3, 1), (2024, "1C")),
        (date(2024, 7, 31), (2024, "1C")),
        (date(2024, 8, 1), (2024, "2C")),
        (date(2024, 12, 31), (2024, "2C")),
    ],
)
def test_date_to_year_term(d: date, expected: tuple[int, str]) -> None:
    assert date_to_year_term(d) == expected
