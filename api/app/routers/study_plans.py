import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.common import PaginatedResponse
from app.schemas.study_plans import StudyPlanCreate, StudyPlanResponse, StudyPlanUpdate
from app.services.study_plans import StudyPlanService

router = APIRouter()

ServiceDep = Annotated[StudyPlanService, Depends(StudyPlanService.dep)]


@router.get("", response_model=PaginatedResponse[StudyPlanResponse])
async def list_study_plans(service: ServiceDep, skip: int = 0, limit: int = 20):
    total, items = await service.list(skip=skip, limit=limit)
    return PaginatedResponse(total=total, items=items)


@router.get("/{plan_id}", response_model=StudyPlanResponse)
async def get_study_plan(plan_id: uuid.UUID, service: ServiceDep):
    return await service.get_by_id(plan_id)


@router.post("", response_model=StudyPlanResponse, status_code=201)
async def create_study_plan(body: StudyPlanCreate, service: ServiceDep):
    return await service.create(body)


@router.put("/{plan_id}", response_model=StudyPlanResponse)
async def update_study_plan(plan_id: uuid.UUID, body: StudyPlanUpdate, service: ServiceDep):
    return await service.update(plan_id, body)


@router.delete("/{plan_id}", status_code=204)
async def delete_study_plan(plan_id: uuid.UUID, service: ServiceDep):
    await service.delete(plan_id)
