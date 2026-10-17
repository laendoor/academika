import uuid
from datetime import date

from pydantic import BaseModel


class _CarreraInfo(BaseModel):
    plan_id: uuid.UUID
    plan_nombre: str
    anio: int
    vigente: bool
    carrera_id: uuid.UUID
    carrera_nombre: str
    estado_academico: str
    fecha_ingreso: date | None


class AlumnoRowResponse(BaseModel):
    id: uuid.UUID
    nombre: str
    apellido: str
    dni: str
    legajo: str | None
    carreras: list[_CarreraInfo]


class PlanInfo(BaseModel):
    plan_id: uuid.UUID
    plan_nombre: str
    anio: int
    vigente: bool
    carrera_id: uuid.UUID
    carrera_nombre: str


class MateriaRowResponse(BaseModel):
    id: uuid.UUID
    nombre: str
    codigo: str
    sigla: str | None
    creditos: int | None
    plan_vigente: PlanInfo | None
    planes: list[PlanInfo]
