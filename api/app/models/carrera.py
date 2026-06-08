from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import AuditMixin, Base, generate_uuid

if TYPE_CHECKING:
    from app.models.plan_de_estudio import PlanDeEstudio


class Carrera(AuditMixin, Base):
    __tablename__ = "carreras"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=generate_uuid)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str] = mapped_column(String(10), unique=True)

    planes: Mapped[list[PlanDeEstudio]] = relationship("PlanDeEstudio", back_populates="carrera")
