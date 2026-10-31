import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import DirectorOrAdminRole
from app.schemas.alumnos import AlumnoCarreraCreate, AlumnoCarreraResponse, AlumnoCreate, AlumnoResponse, AlumnoUpdate
from app.schemas.common import PaginatedResponse, SearchHitResponse
from app.services.alumnos import AlumnoService

router = APIRouter(dependencies=[DirectorOrAdminRole])

ServiceDep = Annotated[AlumnoService, Depends(AlumnoService.dep)]


@router.get("", response_model=PaginatedResponse[AlumnoResponse])
async def list_alumnos(service: ServiceDep, skip: int = 0, limit: int = 20):
    total, items = await service.list(skip=skip, limit=limit)
    return PaginatedResponse(total=total, items=items)


# Antes de /{alumno_id}: si no, "search" se parsea como UUID y devuelve 422.
@router.get("/search", response_model=list[SearchHitResponse])
async def search_alumnos(service: ServiceDep, q: str = Query(min_length=2), limit: int = Query(default=8, le=20)):
    alumnos = await service.search(q, limit)
    return [
        SearchHitResponse(id=a.id, label=f"{a.apellido}, {a.nombre} · DNI {a.dni}", term=f"{a.apellido} {a.nombre}")
        for a in alumnos
    ]


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
