from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import AuditMixin, Base, generate_uuid

if TYPE_CHECKING:
    from app.models.course_enrollment import CourseEnrollment
    from app.models.degree import Degree
    from app.models.study_plan import StudyPlan


class Student(AuditMixin, Base):
    __tablename__ = "student"
    __table_args__ = (UniqueConstraint("legajo", name="uq_student_legajo"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=generate_uuid)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    doc_id: Mapped[str] = mapped_column(String(20), unique=True)
    legajo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    degree_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("degree.id"))
    plan_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(native_uuid=True), ForeignKey("study_plan.id"), nullable=True
    )
    academic_status: Mapped[str] = mapped_column(String(50), ForeignKey("lkp_academic_status.key"))

    degree: Mapped[Degree] = relationship("Degree", back_populates="students")
    study_plan: Mapped[StudyPlan | None] = relationship("StudyPlan")
    course_enrollments: Mapped[list[CourseEnrollment]] = relationship("CourseEnrollment", back_populates="student")
