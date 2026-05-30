from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import AuditMixin, Base, generate_uuid
from app.models.study_plan import study_plan_course

if TYPE_CHECKING:
    from app.models.course_enrollment import CourseEnrollment
    from app.models.course_prerequisite import CoursePrerequisite
    from app.models.study_plan import StudyPlan


class Course(AuditMixin, Base):
    __tablename__ = "course"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(20), unique=True)
    abbreviation: Mapped[str | None] = mapped_column(String(20), nullable=True)

    study_plans: Mapped[list[StudyPlan]] = relationship(
        "StudyPlan", secondary=study_plan_course, back_populates="courses"
    )
    course_enrollments: Mapped[list[CourseEnrollment]] = relationship("CourseEnrollment", back_populates="course")
    prerequisites_as_subject: Mapped[list[CoursePrerequisite]] = relationship(
        "CoursePrerequisite", foreign_keys="CoursePrerequisite.course_id", back_populates="course"
    )
    prerequisites_as_prereq: Mapped[list[CoursePrerequisite]] = relationship(
        "CoursePrerequisite", foreign_keys="CoursePrerequisite.prerequisite_id", back_populates="prerequisite"
    )
