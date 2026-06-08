import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.common import PaginatedResponse
from app.schemas.cursadas import CursadaCreate, CursadaResponse, CursadaUpdate
from app.services.cursadas import CursadaService

router = APIRouter()

ServiceDep = Annotated[CursadaService, Depends(CursadaService.dep)]


@router.get("", response_model=PaginatedResponse[CursadaResponse])
async def list_cursadas(
    service: ServiceDep,
    skip: int = 0,
    limit: int = 20,
    alumno_id: uuid.UUID | None = None,
    materia_id: uuid.UUID | None = None,
    anio: int | None = None,
    cuatrimestre: str | None = None,
):
    total, items = await service.list_filtered(
        skip=skip,
        limit=limit,
        alumno_id=alumno_id,
        materia_id=materia_id,
        anio=anio,
        cuatrimestre=cuatrimestre,
    )
    return PaginatedResponse(total=total, items=items)


@router.get("/{cursada_id}", response_model=CursadaResponse)
async def get_cursada(cursada_id: uuid.UUID, service: ServiceDep):
    return await service.get_by_id(cursada_id)


@router.post("", response_model=CursadaResponse, status_code=201)
async def create_cursada(body: CursadaCreate, service: ServiceDep):
    return await service.create(body)


@router.put("/{cursada_id}", response_model=CursadaResponse)
async def update_cursada(cursada_id: uuid.UUID, body: CursadaUpdate, service: ServiceDep):
    return await service.update(cursada_id, body)


@router.delete("/{cursada_id}", status_code=204)
async def delete_cursada(cursada_id: uuid.UUID, service: ServiceDep):
    await service.delete(cursada_id)
