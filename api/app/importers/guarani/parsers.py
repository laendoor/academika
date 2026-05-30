import logging
from pathlib import Path

from app.importers.utils import or_none, parse_csv, parse_date

from .types import (
    CourseRow,
    DegreeRow,
    EnrollmentHistoryRow,
    EnrollmentRow,
    PrerequisiteRow,
    StudentRow,
    StudyPlanCourseRow,
)

logger = logging.getLogger(__name__)


def parse_degrees(path: Path) -> list[DegreeRow]:
    def _row(row: list[str]) -> DegreeRow:
        code, name, _fecha = row
        return DegreeRow(code=code.strip(), name=name.strip())

    return parse_csv(path, _row)


def parse_courses(path: Path) -> list[CourseRow]:
    def _row(row: list[str]) -> CourseRow:
        _degree_code, _plan_year, code, name, abbreviation = row
        return CourseRow(
            code=code.strip(),
            name=name.strip(),
            abbreviation=or_none(abbreviation),
        )

    return parse_csv(path, _row, has_header=False)


def parse_study_plan_courses(path: Path) -> list[StudyPlanCourseRow]:
    def _row(row: list[str]) -> StudyPlanCourseRow:
        degree_code, plan_year_str, _cuatrimestre, _nucleo, _area, course_code, _creditos, _nombre = row[:8]
        return StudyPlanCourseRow(
            degree_code=degree_code.strip(),
            plan_year=int(plan_year_str.strip()),
            course_code=course_code.strip(),
        )

    return parse_csv(path, _row)


def parse_prerequisites(path: Path) -> list[PrerequisiteRow]:
    def _split_codes(value: str) -> list[str]:
        return [c.strip() for c in value.strip().split(",") if c.strip()]

    def _row(row: list[str]) -> PrerequisiteRow:
        degree_code, plan_year_str, course_code, obligatorias_str, recomendadas_str = row[:5]
        return PrerequisiteRow(
            degree_code=degree_code.strip(),
            plan_year=int(plan_year_str.strip()),
            course_code=course_code.strip(),
            required_codes=_split_codes(obligatorias_str),
            recommended_codes=_split_codes(recomendadas_str),
        )

    return parse_csv(path, _row)


def parse_students(path: Path) -> list[StudentRow]:
    def _row(row: list[str]) -> StudentRow:
        internal_id, doc_id, last_name, first_name, email, date_str, degree_code, plan_year_str = row
        return StudentRow(
            doc_id=doc_id.strip(),
            unq_id=or_none(internal_id),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=or_none(email),
            degree_code=degree_code.strip(),
            study_plan_year=int(plan_year_str.strip()),
            enrolled_at=parse_date(date_str),
        )

    return parse_csv(path, _row)


def parse_enrollment_history(path: Path) -> list[EnrollmentHistoryRow]:
    def _row(row: list[str]) -> EnrollmentHistoryRow:
        (
            _internal_id,
            doc_id,
            degree_code,
            is_regular_str,
            quality,
            course_code,
            _course_name,
            date_str,
            result,
            grade_str,
            approval_type_str,
            credits_str,
            _promo_record,
            _exam_record,
            plan_year_str,
        ) = row
        enrollment_type = "libre" if quality.strip() == "L" else "regular"
        return EnrollmentHistoryRow(
            doc_id=doc_id.strip(),
            degree_code=degree_code.strip(),
            course_code=course_code.strip(),
            is_regular=or_none(is_regular_str),
            enrollment_type=enrollment_type,
            result=result.strip(),
            grade=or_none(grade_str),
            approval_type=or_none(approval_type_str),
            credits=int(credits_str.strip()) if credits_str.strip() else None,
            plan_year=int(plan_year_str.strip()) if plan_year_str.strip() else None,
            enrollment_date=parse_date(date_str),
        )

    return parse_csv(path, _row)


def parse_enrollments(path: Path) -> list[EnrollmentRow]:
    def _row(row: list[str]) -> EnrollmentRow:
        degree_code, doc_id, _internal_id, course_code, section_str, date_str = row
        return EnrollmentRow(
            doc_id=doc_id.strip(),
            degree_code=degree_code.strip(),
            course_code=course_code.strip(),
            section=or_none(section_str),
            enrollment_date=parse_date(date_str),
        )

    return parse_csv(path, _row)
