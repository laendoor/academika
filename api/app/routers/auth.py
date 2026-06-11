from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.dependencies import require_role
from app.schemas.auth import (
    ForgotPasswordRequest,
    InviteRequest,
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
    ResetPasswordRequest,
)
from app.services.auth import AuthService

router = APIRouter()

ServiceDep = Annotated[AuthService, Depends(AuthService.dep)]
AdminRole = Depends(require_role("admin"))


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, service: ServiceDep) -> LoginResponse:
    tokens = await service.login(body.email, body.password)
    return LoginResponse(**tokens)


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(body: RefreshRequest, service: ServiceDep) -> RefreshResponse:
    result = await service.refresh(body.refresh_token)
    return RefreshResponse(**result)


@router.post("/invite", status_code=204, dependencies=[AdminRole])
async def invite(body: InviteRequest, service: ServiceDep) -> None:
    await service.invite(body.email, body.role)


@router.post("/forgot-password", status_code=204)
async def forgot_password(body: ForgotPasswordRequest, service: ServiceDep) -> None:
    await service.forgot_password(body.email)


@router.post("/reset-password", status_code=204)
async def reset_password(body: ResetPasswordRequest, service: ServiceDep) -> None:
    await service.reset_password(body.token, body.new_password)
