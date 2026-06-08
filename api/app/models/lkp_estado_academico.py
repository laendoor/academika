from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LkpEstadoAcademico(Base):
    """Estado académico del alumno en la institución. Tabla de lookup estática."""

    __tablename__ = "lkp_estado_academico"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    label: Mapped[str] = mapped_column(String(100))
