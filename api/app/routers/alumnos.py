import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.alumnos import AlumnoCarreraCreate, AlumnoCarreraResponse, AlumnoCreate, AlumnoResponse, AlumnoUpdate
from app.schemas.common import PaginatedResponse
from app.services.alumnos import AlumnoService

router = APIRouter()

ServiceDep = Annotated[AlumnoService, Depends(AlumnoService.dep)]


@router.get("", response_model=PaginatedResponse[AlumnoResponse])
async def list_alumnos(service: ServiceDep, skip: int = 0, limit: int = 20):
    total, items = await service.list(skip=skip, limit=limit)
    return PaginatedResponse(total=total, items=items)


@router.get("/{alumno_id}", response_model=AlumnoResponse)
async def get_alumno(alumno_id: uuid.UUID, service: ServiceDep):
    return await service.get_by_id(alumno_id)


@router.post("", response_model=AlumnoResponse, status_code=201)
async def create_alumno(body: AlumnoCreate, service: ServiceDep):
    return await service.create(body)


@router.put("/{alumno_id}", response_model=AlumnoResponse)
async def update_alumno(alumno_id: uuid.UUID, body: AlumnoUpdate, service: ServiceDep):
    return await service.update(alumno_id, body)


@router.delete("/{alumno_id}", status_code=204)
async def delete_alumno(alumno_id: uuid.UUID, service: ServiceDep):
    await service.delete(alumno_id)


@router.get("/{alumno_id}/carreras", response_model=list[AlumnoCarreraResponse])
async def list_carreras_de_alumno(alumno_id: uuid.UUID, service: ServiceDep):
    return await service.get_carreras(alumno_id)


@router.post("/{alumno_id}/carreras", response_model=AlumnoCarreraResponse, status_code=201)
async def add_carrera_a_alumno(alumno_id: uuid.UUID, body: AlumnoCarreraCreate, service: ServiceDep):
    return await service.add_carrera(alumno_id, body)
