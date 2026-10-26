import uuid
from datetime import date

from pydantic import BaseModel


class CarreraInfo(BaseModel):
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
    carreras: list[CarreraInfo]


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


class AlumnoRef(BaseModel):
    id: uuid.UUID
    nombre: str
    apellido: str
    legajo: str | None


class MateriaRef(BaseModel):
    id: uuid.UUID
    codigo: str
    nombre: str


class CarreraRef(BaseModel):
    id: uuid.UUID
    codigo: str
    nombre: str


class CursadaRowResponse(BaseModel):
    id: uuid.UUID
    alumno: AlumnoRef
    materia: MateriaRef
    carrera: CarreraRef
    anio: int
    cuatrimestre: str
    comision: str | None
    tipo_cursada: str
    estado_cursada: str
    nota: str | None


class EstudianteDetalleResponse(BaseModel):
    id: uuid.UUID
    nombre: str
    apellido: str
    dni: str
    legajo: str | None
    carreras: list[CarreraInfo]
    cursadas: list[CursadaRowResponse]
