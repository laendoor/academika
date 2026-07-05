import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import require_role
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.users import UserResponse, UserUpdate
from app.services.users import UserService

router = APIRouter()

ServiceDep = Annotated[UserService, Depends(UserService.dep)]
AdminRole = Depends(require_role("admin"))


@router.get("", response_model=PaginatedResponse[UserResponse], dependencies=[AdminRole])
async def list_users(service: ServiceDep, skip: int = 0, limit: int = Query(default=20, le=100)):
    total, items = await service.list(skip=skip, limit=limit)
    return PaginatedResponse(total=total, items=items)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: uuid.UUID, body: UserUpdate, service: ServiceDep, admin: Annotated[User, AdminRole]):
    return await service.update(user_id, body, requester_id=admin.id)
