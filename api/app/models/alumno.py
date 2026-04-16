from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import uuid_utils
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import AuditMixin, Base

if TYPE_CHECKING:
    from app.models.carrera import Carrera
    from app.models.cursada import Cursada
    from app.models.inscripcion import Inscripcion
    from app.models.plan_de_estudio import PlanDeEstudio


class Alumno(AuditMixin, Base):
    __tablename__ = "alumno"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=uuid_utils.uuid7)
    legajo: Mapped[str] = mapped_column(String(32), unique=True)
    nombre: Mapped[str] = mapped_column(String(255))
    apellido: Mapped[str] = mapped_column(String(255))
    dni: Mapped[str] = mapped_column(String(15), unique=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    carrera_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("carrera.id"))
    plan_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(native_uuid=True), ForeignKey("plan_de_estudio.id"), nullable=True
    )
    es_regular: Mapped[bool] = mapped_column(Boolean, default=True)

    carrera: Mapped[Carrera] = relationship("Carrera", back_populates="alumnos")
    plan: Mapped[PlanDeEstudio | None] = relationship("PlanDeEstudio")
    cursadas: Mapped[list[Cursada]] = relationship("Cursada", back_populates="alumno")
    inscripciones: Mapped[list[Inscripcion]] = relationship("Inscripcion", back_populates="alumno")
