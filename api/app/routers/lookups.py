from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.auth.dependencies import get_current_user
from app.db.session import SessionDep
from app.models.lkp_estado_academico import LkpEstadoAcademico
from app.models.lkp_estado_cursada import LkpEstadoCursada
from app.models.lkp_tipo_cursada import LkpTipoCursada
from app.models.lkp_user_role import LkpUserRole
from app.models.user import User
from app.schemas.lookups import (
    EstadoAcademicoResponse,
    EstadoCursadaResponse,
    TipoCursadaResponse,
    UserRoleResponse,
)

router = APIRouter()

AuthDep = Annotated[User, Depends(get_current_user)]


@router.get("/estado-academico", response_model=list[EstadoAcademicoResponse])
async def list_estado_academico(session: SessionDep, _: AuthDep) -> list[LkpEstadoAcademico]:
    result = await session.execute(select(LkpEstadoAcademico))
    return list(result.scalars().all())


@router.get("/estado-cursada", response_model=list[EstadoCursadaResponse])
async def list_estado_cursada(session: SessionDep, _: AuthDep) -> list[LkpEstadoCursada]:
    result = await session.execute(select(LkpEstadoCursada))
    return list(result.scalars().all())


@router.get("/tipo-cursada", response_model=list[TipoCursadaResponse])
async def list_tipo_cursada(session: SessionDep, _: AuthDep) -> list[LkpTipoCursada]:
    result = await session.execute(select(LkpTipoCursada))
    return list(result.scalars().all())


@router.get("/user-roles", response_model=list[UserRoleResponse])
async def list_user_roles(session: SessionDep, _: AuthDep) -> list[LkpUserRole]:
    result = await session.execute(select(LkpUserRole))
    return list(result.scalars().all())
