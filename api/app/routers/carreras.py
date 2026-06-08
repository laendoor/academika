import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.carreras import CarreraCreate, CarreraResponse, CarreraUpdate
from app.schemas.common import PaginatedResponse
from app.services.carreras import CarreraService

router = APIRouter()

ServiceDep = Annotated[CarreraService, Depends(CarreraService.dep)]


@router.get("", response_model=PaginatedResponse[CarreraResponse])
async def list_carreras(service: ServiceDep, skip: int = 0, limit: int = 20):
    total, items = await service.list(skip=skip, limit=limit)
    return PaginatedResponse(total=total, items=items)


@router.get("/{carrera_id}", response_model=CarreraResponse)
async def get_carrera(carrera_id: uuid.UUID, service: ServiceDep):
    return await service.get_by_id(carrera_id)


@router.post("", response_model=CarreraResponse, status_code=201)
async def create_carrera(body: CarreraCreate, service: ServiceDep):
    return await service.create(body)


@router.put("/{carrera_id}", response_model=CarreraResponse)
async def update_carrera(carrera_id: uuid.UUID, body: CarreraUpdate, service: ServiceDep):
    return await service.update(carrera_id, body)


@router.delete("/{carrera_id}", status_code=204)
async def delete_carrera(carrera_id: uuid.UUID, service: ServiceDep):
    await service.delete(carrera_id)
