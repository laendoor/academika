from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import uuid_utils
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import AuditMixin, Base

if TYPE_CHECKING:
    from app.models.carrera import Carrera
    from app.models.materia import Materia

plan_materia = Table(
    "plan_materia",
    Base.metadata,
    Column("plan_id", Uuid(native_uuid=True), ForeignKey("plan_de_estudio.id"), primary_key=True),
    Column("materia_id", Uuid(native_uuid=True), ForeignKey("materia.id"), primary_key=True),
)


class PlanDeEstudio(AuditMixin, Base):
    __tablename__ = "plan_de_estudio"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=uuid_utils.uuid7)
    carrera_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("carrera.id"))
    nombre: Mapped[str] = mapped_column(String(255))
    anio: Mapped[int] = mapped_column(Integer)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    carrera: Mapped[Carrera] = relationship("Carrera", back_populates="planes")
    materias: Mapped[list[Materia]] = relationship("Materia", secondary=plan_materia, back_populates="planes")
