import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.common import PaginatedResponse
from app.schemas.materias import MateriaCreate, MateriaResponse, MateriaUpdate
from app.services.materias import MateriaService

router = APIRouter()

ServiceDep = Annotated[MateriaService, Depends(MateriaService.dep)]


@router.get("", response_model=PaginatedResponse[MateriaResponse])
async def list_materias(service: ServiceDep, skip: int = 0, limit: int = 20):
    total, items = await service.list(skip=skip, limit=limit)
    return PaginatedResponse(total=total, items=items)


@router.get("/{materia_id}", response_model=MateriaResponse)
async def get_materia(materia_id: uuid.UUID, service: ServiceDep):
    return await service.get_by_id(materia_id)


@router.post("", response_model=MateriaResponse, status_code=201)
async def create_materia(body: MateriaCreate, service: ServiceDep):
    return await service.create(body)


@router.put("/{materia_id}", response_model=MateriaResponse)
async def update_materia(materia_id: uuid.UUID, body: MateriaUpdate, service: ServiceDep):
    return await service.update(materia_id, body)


@router.delete("/{materia_id}", status_code=204)
async def delete_materia(materia_id: uuid.UUID, service: ServiceDep):
    await service.delete(materia_id)
