from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import AuditMixin, Base, generate_uuid

if TYPE_CHECKING:
    from app.models.alumno import Alumno
    from app.models.materia import Materia


class Inscripcion(AuditMixin, Base):
    __tablename__ = "inscripcion"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=generate_uuid)
    alumno_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("alumno.id"))
    materia_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("materia.id"))
    periodo: Mapped[str] = mapped_column(String(4))  # e.g. "1C", "2C", "V"
    anio: Mapped[int] = mapped_column(Integer)
    comision: Mapped[str | None] = mapped_column(String(32), nullable=True)
    fecha: Mapped[date | None] = mapped_column(Date, nullable=True)

    alumno: Mapped[Alumno] = relationship("Alumno", back_populates="inscripciones")
    materia: Mapped[Materia] = relationship("Materia")
