import uuid
from datetime import datetime

import uuid_utils as _uuid_utils
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def generate_uuid() -> uuid.UUID:
    """UUID v7 time-ordered como stdlib uuid.UUID (compatible con SQLAlchemy y comparaciones)."""
    return uuid.UUID(str(_uuid_utils.uuid7()))


class Base(DeclarativeBase):
    pass


class AuditMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )
