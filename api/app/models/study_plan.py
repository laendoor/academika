from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import AuditMixin, Base, generate_uuid

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.course_prerequisite import CoursePrerequisite
    from app.models.degree import Degree


study_plan_course = Table(
    "study_plan_course",
    Base.metadata,
    Column("plan_id", Uuid(native_uuid=True), ForeignKey("study_plan.id"), primary_key=True),
    Column("course_id", Uuid(native_uuid=True), ForeignKey("course.id"), primary_key=True),
)


class StudyPlan(AuditMixin, Base):
    __tablename__ = "study_plan"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=generate_uuid)
    degree_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("degree.id"))
    name: Mapped[str] = mapped_column(String(255))
    year: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    __table_args__ = (UniqueConstraint("degree_id", "year", name="uq_study_plan_degree_year"),)

    degree: Mapped[Degree] = relationship("Degree", back_populates="study_plans")
    courses: Mapped[list[Course]] = relationship("Course", secondary=study_plan_course, back_populates="study_plans")
    course_prerequisites: Mapped[list[CoursePrerequisite]] = relationship(
        "CoursePrerequisite", back_populates="plan"
    )
