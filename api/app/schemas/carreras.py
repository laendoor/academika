import uuid
from datetime import datetime

from pydantic import BaseModel


class CarreraCreate(BaseModel):
    nombre: str
    codigo: str


class CarreraUpdate(BaseModel):
    nombre: str | None = None
    codigo: str | None = None


class CarreraResponse(BaseModel):
    id: uuid.UUID
    nombre: str
    codigo: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
