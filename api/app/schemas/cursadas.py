import uuid
from datetime import date, datetime

from pydantic import BaseModel


class CursadaCreate(BaseModel):
    alumno_id: uuid.UUID
    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    anio: int
    cuatrimestre: str
    comision: str | None = None
    tipo_cursada: str
    estado_cursada: str
    nota: str | None = None
    fecha_inscripcion: date | None = None
    fecha_cambio_estado: datetime | None = None
    es_regular: str | None = None
    tipo_aprobacion: str | None = None
    anio_plan: int | None = None


class CursadaUpdate(BaseModel):
    estado_cursada: str | None = None
    nota: str | None = None
    comision: str | None = None
    fecha_cambio_estado: datetime | None = None


class CursadaResponse(BaseModel):
    id: uuid.UUID
    alumno_id: uuid.UUID
    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    anio: int
    cuatrimestre: str
    comision: str | None
    tipo_cursada: str
    estado_cursada: str
    nota: str | None
    fecha_inscripcion: date | None
    fecha_cambio_estado: datetime | None
    es_regular: str | None
    tipo_aprobacion: str | None
    anio_plan: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
