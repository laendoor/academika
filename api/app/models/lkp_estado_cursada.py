from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LkpEstadoCursada(Base):
    """Estado de una cursada. Tabla de lookup estática.

    Valores: inscripto (I), regular (R), promocionado (P), aprobado (A), pendiente_aprobacion (PA).
    """

    __tablename__ = "lkp_estado_cursada"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    code: Mapped[str] = mapped_column(String(5), unique=True)
    label: Mapped[str] = mapped_column(String(100))
