import uuid
from datetime import datetime

from pydantic import BaseModel


class PlanDeEstudioCreate(BaseModel):
    carrera_id: uuid.UUID
    nombre: str
    anio: int
    vigente: bool = True
    materia_ids: list[uuid.UUID] = []


class PlanDeEstudioUpdate(BaseModel):
    nombre: str | None = None
    anio: int | None = None
    vigente: bool | None = None
    materia_ids: list[uuid.UUID] | None = None


class PlanDeEstudioResponse(BaseModel):
    id: uuid.UUID
    carrera_id: uuid.UUID
    nombre: str
    anio: int
    vigente: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MateriaEnPlan(BaseModel):
    id: uuid.UUID
    codigo: str
    sigla: str | None
    nombre: str
    creditos: int | None
    nucleo: str | None
    horas_semanales: int | None
    carga_horaria_total: int | None


class PlanDeEstudioDetail(BaseModel):
    id: uuid.UUID
    carrera_id: uuid.UUID
    carrera_nombre: str
    nombre: str
    nivel: str | None
    anio: int
    vigente: bool
    materias: list[MateriaEnPlan]
    created_at: datetime
    updated_at: datetime
