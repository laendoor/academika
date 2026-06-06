from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.types import Uuid

from app.db.base import Base

study_plans_courses = Table(
    "study_plans_courses",
    Base.metadata,
    Column("plan_id", Uuid(native_uuid=True), ForeignKey("study_plans.id"), primary_key=True),
    Column("course_id", Uuid(native_uuid=True), ForeignKey("courses.id"), primary_key=True),
)
