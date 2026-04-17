from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import AuditMixin, Base, generate_uuid

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.study_plan import StudyPlan


class Degree(AuditMixin, Base):
    __tablename__ = "degree"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(10), unique=True)

    students: Mapped[list[Student]] = relationship("Student", back_populates="degree")
    study_plans: Mapped[list[StudyPlan]] = relationship("StudyPlan", back_populates="degree")
