import uuid
from datetime import date, datetime

from pydantic import BaseModel


class CourseEnrollmentCreate(BaseModel):
    student_id: uuid.UUID
    course_id: uuid.UUID
    degree_id: uuid.UUID
    year: int
    term: str
    section: str | None = None
    enrollment_type: str
    enrollment_status: str
    grade: str | None = None
    enrolled_at: date | None = None
    status_changed_at: datetime | None = None
    is_regular: str | None = None
    approval_type: str | None = None
    credits: int | None = None
    plan_year: int | None = None


class CourseEnrollmentUpdate(BaseModel):
    enrollment_status: str | None = None
    grade: str | None = None
    section: str | None = None
    status_changed_at: datetime | None = None


class CourseEnrollmentResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    course_id: uuid.UUID
    degree_id: uuid.UUID
    year: int
    term: str
    section: str | None
    enrollment_type: str
    enrollment_status: str
    grade: str | None
    enrolled_at: date | None
    status_changed_at: datetime | None
    is_regular: str | None
    approval_type: str | None
    credits: int | None
    plan_year: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
