from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import uuid_utils
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.db.base import AuditMixin, Base
from app.models.plan_de_estudio import plan_materia

if TYPE_CHECKING:
    from app.models.plan_de_estudio import PlanDeEstudio


class Materia(AuditMixin, Base):
    __tablename__ = "materia"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=uuid_utils.uuid7)
    nombre: Mapped[str] = mapped_column(String(255))
    codigo: Mapped[str] = mapped_column(String(32), unique=True)
    siglas: Mapped[str | None] = mapped_column(String(32), nullable=True)

    planes: Mapped[list[PlanDeEstudio]] = relationship(
        "PlanDeEstudio", secondary=plan_materia, back_populates="materias"
    )
