from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import AuditMixin, Base

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.study_plan import StudyPlan


class CoursePrerequisite(AuditMixin, Base):
    __tablename__ = "course_prerequisite"

    plan_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("study_plan.id"), primary_key=True)
    course_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("course.id"), primary_key=True)
    prerequisite_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(native_uuid=True), ForeignKey("course.id"), primary_key=True
    )
    is_required: Mapped[bool] = mapped_column(Boolean)

    plan: Mapped[StudyPlan] = relationship("StudyPlan", back_populates="course_prerequisites")
    course: Mapped[Course] = relationship("Course", foreign_keys=[course_id], back_populates="prerequisites_as_subject")
    prerequisite: Mapped[Course] = relationship(
        "Course", foreign_keys=[prerequisite_id], back_populates="prerequisites_as_prereq"
    )
