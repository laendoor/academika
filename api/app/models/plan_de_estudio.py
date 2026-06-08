from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import AuditMixin, Base, generate_uuid
from app.models.planes_materias import planes_materias

if TYPE_CHECKING:
    from app.models.carrera import Carrera
    from app.models.materia import Materia


class PlanDeEstudio(AuditMixin, Base):
    __tablename__ = "planes_de_estudio"
    __table_args__ = (UniqueConstraint("carrera_id", "anio", name="uq_plan_carrera_anio"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=generate_uuid)
    carrera_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("carreras.id"))
    nombre: Mapped[str] = mapped_column(String(255))
    nivel: Mapped[str | None] = mapped_column(String(50), ForeignKey("lkp_nivel_carrera.key"), nullable=True)
    anio: Mapped[int] = mapped_column(Integer)
    vigente: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    carrera: Mapped[Carrera] = relationship("Carrera", back_populates="planes")
    materias: Mapped[list[Materia]] = relationship("Materia", secondary=planes_materias, back_populates="planes")
