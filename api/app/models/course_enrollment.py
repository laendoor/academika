from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import AuditMixin, Base, generate_uuid

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.degree import Degree
    from app.models.student import Student


class CourseEnrollment(AuditMixin, Base):
    """Inscripción de un estudiante a una cursada (regular o libre).

    Fusiona Cursada e Inscripcion: cubre tanto el momento de inscripción
    como el estado final (regular, aprobado, etc.).
    """

    __tablename__ = "course_enrollment"
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "course_id",
            "degree_id",
            "year",
            "term",
            name="uq_enrollment_student_course_degree_term",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=generate_uuid)
    student_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("student.id"))
    course_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("course.id"))
    degree_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("degree.id"))
    year: Mapped[int] = mapped_column(Integer)
    term: Mapped[str] = mapped_column(String(5))  # "1C", "2C"
    section: Mapped[str | None] = mapped_column(String(20), nullable=True)
    enrollment_type: Mapped[str] = mapped_column(String(50), ForeignKey("lkp_enrollment_type.key"))
    enrollment_status: Mapped[str] = mapped_column(String(50), ForeignKey("lkp_enrollment_status.key"))
    grade: Mapped[str | None] = mapped_column(String(5), nullable=True)
    enrolled_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    status_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_regular: Mapped[str | None] = mapped_column(String(5), nullable=True)
    approval_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    credits: Mapped[int | None] = mapped_column(Integer, nullable=True)
    plan_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    student: Mapped[Student] = relationship("Student", back_populates="course_enrollments")
    course: Mapped[Course] = relationship("Course", back_populates="course_enrollments")
    degree: Mapped[Degree] = relationship("Degree")
