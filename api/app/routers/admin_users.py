import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import AdminRole, CurrentUser
from app.schemas.common import PaginatedResponse
from app.schemas.users import UserResponse, UserUpdate
from app.services.users import UserService

router = APIRouter()

ServiceDep = Annotated[UserService, Depends(UserService.dep)]


@router.get("", response_model=PaginatedResponse[UserResponse], dependencies=[AdminRole])
async def list_users(service: ServiceDep, skip: int = 0, limit: int = Query(default=20, le=100)):
    total, items = await service.list(skip=skip, limit=limit)
    return PaginatedResponse(total=total, items=items)


@router.put("/{user_id}", response_model=UserResponse, dependencies=[AdminRole])
async def update_user(user_id: uuid.UUID, body: UserUpdate, service: ServiceDep, admin: CurrentUser):
    return await service.update(user_id, body, requester_id=admin.id)


@router.delete("/{user_id}", status_code=204, dependencies=[AdminRole])
async def delete_user(user_id: uuid.UUID, service: ServiceDep, admin: CurrentUser):
    await service.delete(user_id, requester_id=admin.id)
