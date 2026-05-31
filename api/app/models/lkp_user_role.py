from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LkpUserRole(Base):
    """Rol de usuario. Tabla de lookup estática.

    Valores: admin (administrador del sistema), director (director de carrera).
    """

    __tablename__ = "lkp_user_roles"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    label: Mapped[str] = mapped_column(String(100))
