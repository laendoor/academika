from dataclasses import dataclass, field
from datetime import date


@dataclass
class DegreeRow:
    code: str
    name: str


@dataclass
class CourseRow:
    code: str
    name: str
    abbreviation: str | None


@dataclass
class StudyPlanCourseRow:
    degree_code: str
    plan_year: int
    course_code: str


@dataclass
class PrerequisiteRow:
    degree_code: str
    plan_year: int
    course_code: str
    required_codes: list[str] = field(default_factory=list)
    recommended_codes: list[str] = field(default_factory=list)


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
