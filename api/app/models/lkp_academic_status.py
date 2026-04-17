from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LkpAcademicStatus(Base):
    """Estado académico del estudiante en la institución. Tabla de lookup estática."""

    __tablename__ = "lkp_academic_status"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    label: Mapped[str] = mapped_column(String(100))
