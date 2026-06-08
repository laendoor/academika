from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import AuditMixin, Base

if TYPE_CHECKING:
    from app.models.alumno import Alumno
    from app.models.plan_de_estudio import PlanDeEstudio


class AlumnoCarrera(AuditMixin, Base):
    """Inscripción de un alumno en una carrera. Un alumno puede estar en más de una."""

    __tablename__ = "alumno_carrera"

    alumno_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("alumnos.id"), primary_key=True)
    plan_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(native_uuid=True), ForeignKey("planes_de_estudio.id"), primary_key=True
    )
    fecha_ingreso: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado_academico: Mapped[str] = mapped_column(String(50), ForeignKey("lkp_estado_academico.key"))

    alumno: Mapped[Alumno] = relationship("Alumno", back_populates="carreras")
    plan: Mapped[PlanDeEstudio] = relationship("PlanDeEstudio")
