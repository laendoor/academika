from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import uuid_utils
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import AuditMixin, Base

if TYPE_CHECKING:
    from app.models.alumno import Alumno
    from app.models.plan_de_estudio import PlanDeEstudio


class Carrera(AuditMixin, Base):
    __tablename__ = "carrera"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=uuid_utils.uuid7)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str] = mapped_column(String(10), unique=True)

    alumnos: Mapped[list[Alumno]] = relationship("Alumno", back_populates="carrera")
    planes: Mapped[list[PlanDeEstudio]] = relationship("PlanDeEstudio", back_populates="carrera")
