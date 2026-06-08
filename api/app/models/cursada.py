from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import AuditMixin, Base, generate_uuid

if TYPE_CHECKING:
    from app.models.alumno import Alumno
    from app.models.carrera import Carrera
    from app.models.materia import Materia


class Cursada(AuditMixin, Base):
    """Inscripción de un alumno a una cursada (regular o libre).

    Fusiona Cursada e Inscripcion: cubre tanto el momento de inscripción
    como el estado final (regular, aprobado, etc.).
    """

    __tablename__ = "cursadas"
    __table_args__ = (
        UniqueConstraint(
            "alumno_id",
            "materia_id",
            "carrera_id",
            "anio",
            "cuatrimestre",
            name="uq_cursada_alumno_materia_carrera_cuatrimestre",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=generate_uuid)
    alumno_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("alumnos.id"))
    materia_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("materias.id"))
    carrera_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("carreras.id"))
    anio: Mapped[int] = mapped_column(Integer)
    cuatrimestre: Mapped[str] = mapped_column(String(5))
    comision: Mapped[str | None] = mapped_column(String(20), nullable=True)
    tipo_cursada: Mapped[str] = mapped_column(String(50), ForeignKey("lkp_tipo_cursada.key"))
    estado_cursada: Mapped[str] = mapped_column(String(50), ForeignKey("lkp_estado_cursada.key"))
    nota: Mapped[str | None] = mapped_column(String(5), nullable=True)
    fecha_inscripcion: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_cambio_estado: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    es_regular: Mapped[str | None] = mapped_column(String(5), nullable=True)
    tipo_aprobacion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    anio_plan: Mapped[int | None] = mapped_column(Integer, nullable=True)

    alumno: Mapped[Alumno] = relationship("Alumno", back_populates="cursadas")
    materia: Mapped[Materia] = relationship("Materia", back_populates="cursadas")
    carrera: Mapped[Carrera] = relationship("Carrera")
