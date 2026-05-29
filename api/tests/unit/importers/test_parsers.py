from datetime import date
from pathlib import Path

import pytest

from app.importers.guarani.parsers import (
    parse_courses,
    parse_degrees,
    parse_enrollment_history,
    parse_enrollments,
    parse_prerequisites,
    parse_study_plan_courses,
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


class TestParseCarreras:
    def test_parses_valid_rows(self) -> None:
        rows = parse_degrees(FIXTURES / "carreras.csv")
        assert len(rows) == 2

    def test_fields(self) -> None:
        row = parse_degrees(FIXTURES / "carreras.csv")[0]
        assert row.code == "TPI"
        assert row.name == "Tecnicatura Universitaria en Programación Informática"

    def test_skips_invalid_row(self) -> None:
        rows = parse_degrees(FIXTURES / "carreras.csv")
        assert len(rows) == 2


class TestParseMaterias:
    def test_parses_valid_rows(self) -> None:
        rows = parse_courses(FIXTURES / "materias.csv")
        assert len(rows) == 3

    def test_fields(self) -> None:
        row = parse_courses(FIXTURES / "materias.csv")[0]
        assert row.code == "101"
        assert row.name == "Algoritmos"
        assert row.abbreviation == "algo"

    def test_optional_abbreviation_is_none(self) -> None:
        rows = parse_courses(FIXTURES / "materias.csv")
        assert rows[2].abbreviation is None


class TestParsePlanes:
    def test_parses_valid_rows(self) -> None:
        rows = parse_study_plan_courses(FIXTURES / "planes.csv")
        assert len(rows) == 3

    def test_fields(self) -> None:
        row = parse_study_plan_courses(FIXTURES / "planes.csv")[0]
        assert row.degree_code == "TPI"
        assert row.plan_year == 2015
        assert row.course_code == "101"

    def test_multiple_degrees(self) -> None:
        rows = parse_study_plan_courses(FIXTURES / "planes.csv")
        assert rows[2].degree_code == "LDS"
        assert rows[2].plan_year == 2018


class TestParseRequisitos:
    def test_parses_valid_rows(self) -> None:
        rows = parse_prerequisites(FIXTURES / "requisitos.csv")
        assert len(rows) == 3

    def test_single_required(self) -> None:
        row = parse_prerequisites(FIXTURES / "requisitos.csv")[0]
        assert row.course_code == "102"
        assert row.required_codes == ["101"]
        assert row.recommended_codes == []

    def test_multiple_required_and_recommended(self) -> None:
        row = parse_prerequisites(FIXTURES / "requisitos.csv")[1]
        assert row.course_code == "103"
        assert row.required_codes == ["101", "102"]
        assert row.recommended_codes == ["101"]

    def test_no_prerequisites(self) -> None:
        row = parse_prerequisites(FIXTURES / "requisitos.csv")[2]
        assert row.required_codes == []
        assert row.recommended_codes == []


@pytest.mark.parametrize(
    "d,expected",
    [
        (date(2024, 1, 15), (2024, "1C")),
        (date(2024, 2, 28), (2024, "1C")),
        (date(2024, 3, 1), (2024, "1C")),
        (date(2024, 6, 30), (2024, "1C")),
        (date(2024, 7, 1), (2024, "2C")),
        (date(2024, 7, 31), (2024, "2C")),
        (date(2024, 8, 1), (2024, "2C")),
        (date(2024, 12, 31), (2024, "2C")),
    ],
)
def test_date_to_year_term(d: date, expected: tuple[int, str]) -> None:
    assert date_to_year_term(d) == expected
