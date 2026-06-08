from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LkpNucleoCarrera(Base):
    """Núcleo académico al que pertenece una materia dentro de un plan."""

    __tablename__ = "lkp_nucleo_carrera"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    label: Mapped[str] = mapped_column(String(100))
