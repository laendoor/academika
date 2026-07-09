from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LkpLogAction(Base):
    """Acción de log. Tabla de lookup estática.

    Valores: import_guarani (importación de planillas Guaraní).
    """

    __tablename__ = "lkp_log_action"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    label: Mapped[str] = mapped_column(String(100))
