from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Computed, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from db.base import AuditMixin, Base, generate_uuid
from db.models.planes_materias import planes_materias
from db.search import MATERIA_SEARCH_TERM

if TYPE_CHECKING:
    from db.models.correlativa import Correlativa
    from db.models.cursada import Cursada
    from db.models.plan_de_estudio import PlanDeEstudio


class Materia(AuditMixin, Base):
    __tablename__ = "materias"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=generate_uuid)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    sigla: Mapped[str | None] = mapped_column(String(20), nullable=True)
    creditos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nucleo: Mapped[str | None] = mapped_column(String(50), ForeignKey("lkp_nucleo_carrera.key"), nullable=True)
    horas_semanales: Mapped[int | None] = mapped_column(Integer, nullable=True)
    carga_horaria_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Normalizado (sin tildes, minúsculas) para buscar; no sirve para mostrar.
    search_term: Mapped[str] = mapped_column(Text, Computed(MATERIA_SEARCH_TERM, persisted=True))

    planes: Mapped[list[PlanDeEstudio]] = relationship(
        "PlanDeEstudio", secondary=planes_materias, back_populates="materias"
    )
    cursadas: Mapped[list[Cursada]] = relationship("Cursada", back_populates="materia")
    materias_requeridas: Mapped[list[Correlativa]] = relationship(
        "Correlativa", foreign_keys="Correlativa.materia_id", back_populates="materia"
    )
    requerida_por: Mapped[list[Correlativa]] = relationship(
        "Correlativa", foreign_keys="Correlativa.requisito_id", back_populates="requisito"
    )
