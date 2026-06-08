import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.common import PaginatedResponse
from app.schemas.planes_de_estudio import PlanDeEstudioCreate, PlanDeEstudioResponse, PlanDeEstudioUpdate
from app.services.planes_de_estudio import PlanDeEstudioService

router = APIRouter()

ServiceDep = Annotated[PlanDeEstudioService, Depends(PlanDeEstudioService.dep)]


@router.get("", response_model=PaginatedResponse[PlanDeEstudioResponse])
async def list_planes(service: ServiceDep, skip: int = 0, limit: int = 20):
    total, items = await service.list(skip=skip, limit=limit)
    return PaginatedResponse(total=total, items=items)


@router.get("/{plan_id}", response_model=PlanDeEstudioResponse)
async def get_plan(plan_id: uuid.UUID, service: ServiceDep):
    return await service.get_by_id(plan_id)


@router.post("", response_model=PlanDeEstudioResponse, status_code=201)
async def create_plan(body: PlanDeEstudioCreate, service: ServiceDep):
    return await service.create(body)


@router.put("/{plan_id}", response_model=PlanDeEstudioResponse)
async def update_plan(plan_id: uuid.UUID, body: PlanDeEstudioUpdate, service: ServiceDep):
    return await service.update(plan_id, body)


@router.delete("/{plan_id}", status_code=204)
async def delete_plan(plan_id: uuid.UUID, service: ServiceDep):
    await service.delete(plan_id)
