from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Computed, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from db.base import AuditMixin, Base, generate_uuid
from db.search import ALUMNO_SEARCH_TERM

if TYPE_CHECKING:
    from db.models.alumno_carrera import AlumnoCarrera
    from db.models.cursada import Cursada


class Alumno(AuditMixin, Base):
    __tablename__ = "alumnos"
    __table_args__ = (UniqueConstraint("legajo", name="uq_alumno_legajo"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=generate_uuid)
    nombre: Mapped[str] = mapped_column(String(100))
    apellido: Mapped[str] = mapped_column(String(100))
    dni: Mapped[str] = mapped_column(String(20), unique=True)
    legajo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Normalizado (sin tildes, minúsculas) para buscar; no sirve para mostrar.
    search_term: Mapped[str] = mapped_column(Text, Computed(ALUMNO_SEARCH_TERM, persisted=True))

    carreras: Mapped[list[AlumnoCarrera]] = relationship("AlumnoCarrera", back_populates="alumno")
    cursadas: Mapped[list[Cursada]] = relationship("Cursada", back_populates="alumno")
