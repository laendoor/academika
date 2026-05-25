from dataclasses import dataclass
from datetime import date


@dataclass
class StudentRow:
    doc_id: str
    unq_id: str | None
    first_name: str
    last_name: str
    email: str | None
    degree_code: str
    study_plan_year: int
    enrolled_at: date


@dataclass
class EnrollmentHistoryRow:
    doc_id: str
    degree_code: str
    course_code: str
    is_regular: str | None
    enrollment_type: str
    result: str
    grade: str | None
    approval_type: str | None
    credits: int | None
    plan_year: int | None
    enrollment_date: date


@dataclass
class EnrollmentRow:
    doc_id: str
    degree_code: str
    course_code: str
    section: str | None
    enrollment_date: date
