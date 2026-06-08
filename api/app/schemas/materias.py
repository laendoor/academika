import uuid
from datetime import datetime

from pydantic import BaseModel


class MateriaCreate(BaseModel):
    nombre: str
    codigo: str
    sigla: str | None = None
    creditos: int | None = None


class MateriaUpdate(BaseModel):
    nombre: str | None = None
    codigo: str | None = None
    sigla: str | None = None
    creditos: int | None = None


class MateriaResponse(BaseModel):
    id: uuid.UUID
    nombre: str
    codigo: str
    sigla: str | None
    creditos: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
