from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LkpNivelCarrera(Base):
    """Nivel académico de un plan de estudios (grado, pregrado)."""

    __tablename__ = "lkp_nivel_carrera"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    label: Mapped[str] = mapped_column(String(100))
