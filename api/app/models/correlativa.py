from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import AuditMixin, Base

if TYPE_CHECKING:
    from app.models.materia import Materia


class Correlativa(AuditMixin, Base):
    __tablename__ = "correlativas"

    materia_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("materias.id"), primary_key=True)
    requisito_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("materias.id"), primary_key=True)
    es_obligatoria: Mapped[bool] = mapped_column(Boolean)

    materia: Mapped[Materia] = relationship("Materia", foreign_keys=[materia_id], back_populates="materias_requeridas")
    requisito: Mapped[Materia] = relationship("Materia", foreign_keys=[requisito_id], back_populates="requerida_por")
