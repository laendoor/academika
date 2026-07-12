from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.db.base import Base, generate_uuid


class LogEvent(Base):
    """Evento de log transversal. Una fila por acción registrada.

    `details` es JSONB genérico; el tipado por `action` vive en Pydantic
    (ver `app.schemas.log_events`).
    """

    __tablename__ = "log_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), primary_key=True, default=generate_uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), server_default=func.now())
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(native_uuid=True), ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(50), ForeignKey("lkp_log_action.key"))
    status: Mapped[str] = mapped_column(String(50), ForeignKey("lkp_log_status.key"))
    details: Mapped[dict] = mapped_column(JSONB)
