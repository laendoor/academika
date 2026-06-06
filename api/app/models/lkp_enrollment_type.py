from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LkpEnrollmentType(Base):
    """Modalidad de cursada. Tabla de lookup estática.

    Valores: regular (cursada presencial), libre (solo examen final).
    """

    __tablename__ = "lkp_enrollment_types"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    label: Mapped[str] = mapped_column(String(100))
