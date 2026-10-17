import uuid
from typing import Annotated

from db.models.plan_de_estudio import PlanDeEstudio
from fastapi import APIRouter, Depends

from app.auth.dependencies import DirectorOrAdminRole
from app.schemas.common import PaginatedResponse
from app.schemas.planes_de_estudio import (
    MateriaEnPlan,
    PlanDeEstudioCreate,
    PlanDeEstudioDetail,
    PlanDeEstudioResponse,
    PlanDeEstudioRow,
    PlanDeEstudioUpdate,
)
from app.services.planes_de_estudio import PlanDeEstudioService

router = APIRouter(dependencies=[DirectorOrAdminRole])

ServiceDep = Annotated[PlanDeEstudioService, Depends(PlanDeEstudioService.dep)]


@router.get("", response_model=PaginatedResponse[PlanDeEstudioRow])
async def list_planes(service: ServiceDep, skip: int = 0, limit: int = 20, carrera_id: uuid.UUID | None = None):
    total, items = await service.list_filtered(skip=skip, limit=limit, carrera_id=carrera_id)
    return PaginatedResponse(total=total, items=[_to_row(plan) for plan in items])


@router.get("/{plan_id}", response_model=PlanDeEstudioDetail)
async def get_plan(plan_id: uuid.UUID, service: ServiceDep):
    return _to_detail(await service.get_detail(plan_id))


def _to_row(plan: PlanDeEstudio) -> PlanDeEstudioRow:
    return PlanDeEstudioRow(
        id=plan.id,
        carrera_id=plan.carrera_id,
        carrera_nombre=plan.carrera.nombre,
        nombre=plan.nombre,
        nivel=plan.nivel,
        anio=plan.anio,
        vigente=plan.vigente,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


def _to_detail(plan: PlanDeEstudio) -> PlanDeEstudioDetail:
    return PlanDeEstudioDetail(
        id=plan.id,
        carrera_id=plan.carrera_id,
        carrera_nombre=plan.carrera.nombre,
        nombre=plan.nombre,
        nivel=plan.nivel,
        anio=plan.anio,
        vigente=plan.vigente,
        materias=[MateriaEnPlan.model_validate(m) for m in sorted(plan.materias, key=lambda m: m.nombre)],
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


@router.post("", response_model=PlanDeEstudioResponse, status_code=201)
async def create_plan(body: PlanDeEstudioCreate, service: ServiceDep):
    return await service.create(body)


@router.put("/{plan_id}", response_model=PlanDeEstudioResponse)
async def update_plan(plan_id: uuid.UUID, body: PlanDeEstudioUpdate, service: ServiceDep):
    return await service.update(plan_id, body)


@router.delete("/{plan_id}", status_code=204)
async def delete_plan(plan_id: uuid.UUID, service: ServiceDep):
    await service.delete(plan_id)
