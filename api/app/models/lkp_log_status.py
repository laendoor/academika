from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LkpLogStatus(Base):
    """Estado de un log event. Tabla de lookup estática.

    Valores: ok, processing, error.
    """

    __tablename__ = "lkp_log_status"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    label: Mapped[str] = mapped_column(String(100))
