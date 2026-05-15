import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.common import PaginatedResponse
from app.schemas.courses import CourseCreate, CourseResponse, CourseUpdate
from app.services.courses import CourseService

router = APIRouter()

ServiceDep = Annotated[CourseService, Depends(CourseService.dep)]


@router.get("", response_model=PaginatedResponse[CourseResponse])
async def list_courses(service: ServiceDep, skip: int = 0, limit: int = 20):
    total, items = await service.list(skip=skip, limit=limit)
    return PaginatedResponse(total=total, items=items)


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: uuid.UUID, service: ServiceDep):
    return await service.get_by_id(course_id)


@router.post("", response_model=CourseResponse, status_code=201)
async def create_course(body: CourseCreate, service: ServiceDep):
    return await service.create(body)


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(course_id: uuid.UUID, body: CourseUpdate, service: ServiceDep):
    return await service.update(course_id, body)


@router.delete("/{course_id}", status_code=204)
async def delete_course(course_id: uuid.UUID, service: ServiceDep):
    await service.delete(course_id)
