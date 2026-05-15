import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.common import PaginatedResponse
from app.schemas.course_enrollments import (
    CourseEnrollmentCreate,
    CourseEnrollmentResponse,
    CourseEnrollmentUpdate,
)
from app.services.course_enrollments import CourseEnrollmentService

router = APIRouter()

ServiceDep = Annotated[CourseEnrollmentService, Depends(CourseEnrollmentService.dep)]


@router.get("", response_model=PaginatedResponse[CourseEnrollmentResponse])
async def list_course_enrollments(
    service: ServiceDep,
    skip: int = 0,
    limit: int = 20,
    student_id: uuid.UUID | None = None,
    course_id: uuid.UUID | None = None,
    year: int | None = None,
    term: str | None = None,
):
    total, items = await service.list_filtered(
        skip=skip,
        limit=limit,
        student_id=student_id,
        course_id=course_id,
        year=year,
        term=term,
    )
    return PaginatedResponse(total=total, items=items)


@router.get("/{enrollment_id}", response_model=CourseEnrollmentResponse)
async def get_course_enrollment(enrollment_id: uuid.UUID, service: ServiceDep):
    return await service.get_by_id(enrollment_id)


@router.post("", response_model=CourseEnrollmentResponse, status_code=201)
async def create_course_enrollment(body: CourseEnrollmentCreate, service: ServiceDep):
    return await service.create(body)


@router.put("/{enrollment_id}", response_model=CourseEnrollmentResponse)
async def update_course_enrollment(
    enrollment_id: uuid.UUID, body: CourseEnrollmentUpdate, service: ServiceDep
):
    return await service.update(enrollment_id, body)


@router.delete("/{enrollment_id}", status_code=204)
async def delete_course_enrollment(enrollment_id: uuid.UUID, service: ServiceDep):
    await service.delete(enrollment_id)
