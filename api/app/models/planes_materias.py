from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.types import Uuid

from app.db.base import Base

planes_materias = Table(
    "planes_materias",
    Base.metadata,
    Column("plan_id", Uuid(native_uuid=True), ForeignKey("planes_de_estudio.id"), primary_key=True),
    Column("materia_id", Uuid(native_uuid=True), ForeignKey("materias.id"), primary_key=True),
)
