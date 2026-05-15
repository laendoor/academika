import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.common import PaginatedResponse
from app.schemas.degrees import DegreeCreate, DegreeResponse, DegreeUpdate
from app.services.degrees import DegreeService

router = APIRouter()

ServiceDep = Annotated[DegreeService, Depends(DegreeService.dep)]


@router.get("", response_model=PaginatedResponse[DegreeResponse])
async def list_degrees(service: ServiceDep, skip: int = 0, limit: int = 20):
    total, items = await service.list(skip=skip, limit=limit)
    return PaginatedResponse(total=total, items=items)


@router.get("/{degree_id}", response_model=DegreeResponse)
async def get_degree(degree_id: uuid.UUID, service: ServiceDep):
    return await service.get_by_id(degree_id)


@router.post("", response_model=DegreeResponse, status_code=201)
async def create_degree(body: DegreeCreate, service: ServiceDep):
    return await service.create(body)


@router.put("/{degree_id}", response_model=DegreeResponse)
async def update_degree(degree_id: uuid.UUID, body: DegreeUpdate, service: ServiceDep):
    return await service.update(degree_id, body)


@router.delete("/{degree_id}", status_code=204)
async def delete_degree(degree_id: uuid.UUID, service: ServiceDep):
    await service.delete(degree_id)
