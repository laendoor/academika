import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.common import PaginatedResponse
from app.schemas.students import StudentCreate, StudentResponse, StudentUpdate
from app.services.students import StudentService

router = APIRouter()

ServiceDep = Annotated[StudentService, Depends(StudentService.dep)]


@router.get("", response_model=PaginatedResponse[StudentResponse])
async def list_students(service: ServiceDep, skip: int = 0, limit: int = 20):
    total, items = await service.list(skip=skip, limit=limit)
    return PaginatedResponse(total=total, items=items)


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: uuid.UUID, service: ServiceDep):
    return await service.get_by_id(student_id)


@router.post("", response_model=StudentResponse, status_code=201)
async def create_student(body: StudentCreate, service: ServiceDep):
    return await service.create(body)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(student_id: uuid.UUID, body: StudentUpdate, service: ServiceDep):
    return await service.update(student_id, body)


@router.delete("/{student_id}", status_code=204)
async def delete_student(student_id: uuid.UUID, service: ServiceDep):
    await service.delete(student_id)
