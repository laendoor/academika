import uuid
from datetime import date, datetime

from pydantic import BaseModel


class AlumnoCreate(BaseModel):
    nombre: str
    apellido: str
    dni: str
    email: str | None = None


class AlumnoUpdate(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    email: str | None = None


class AlumnoResponse(BaseModel):
    id: uuid.UUID
    nombre: str
    apellido: str
    dni: str
    email: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlumnoCarreraCreate(BaseModel):
    plan_id: uuid.UUID
    fecha_ingreso: date | None = None
    estado_academico: str


class AlumnoCarreraResponse(BaseModel):
    alumno_id: uuid.UUID
    plan_id: uuid.UUID
    fecha_ingreso: date | None
    estado_academico: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
