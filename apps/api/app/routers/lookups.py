from typing import Annotated

from db.base import Base
from db.models.lkp_estado_academico import LkpEstadoAcademico
from db.models.lkp_estado_cursada import LkpEstadoCursada
from db.models.lkp_nivel_carrera import LkpNivelCarrera
from db.models.lkp_nucleo_carrera import LkpNucleoCarrera
from db.models.lkp_tipo_cursada import LkpTipoCursada
from db.models.lkp_user_role import LkpUserRole
from db.models.user import User
from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.auth.dependencies import get_current_user
from app.schemas.lookups import (
    EstadoAcademicoResponse,
    EstadoCursadaResponse,
    NivelCarreraResponse,
    NucleoCarreraResponse,
    TipoCursadaResponse,
    UserRoleResponse,
)
from app.session import SessionDep

router = APIRouter()

AuthDep = Annotated[User, Depends(get_current_user)]


async def _list_entries(session: SessionDep, model: type[Base]) -> list:
    result = await session.execute(select(model).order_by(model.key))
    return list(result.scalars().all())


@router.get("/estado-academico", response_model=list[EstadoAcademicoResponse])
async def list_estado_academico(session: SessionDep, _: AuthDep) -> list[EstadoAcademicoResponse]:
    return await _list_entries(session, LkpEstadoAcademico)


@router.get("/estado-cursada", response_model=list[EstadoCursadaResponse])
async def list_estado_cursada(session: SessionDep, _: AuthDep) -> list[EstadoCursadaResponse]:
    return await _list_entries(session, LkpEstadoCursada)


@router.get("/tipo-cursada", response_model=list[TipoCursadaResponse])
async def list_tipo_cursada(session: SessionDep, _: AuthDep) -> list[TipoCursadaResponse]:
    return await _list_entries(session, LkpTipoCursada)


@router.get("/user-roles", response_model=list[UserRoleResponse])
async def list_user_roles(session: SessionDep, _: AuthDep) -> list[UserRoleResponse]:
    return await _list_entries(session, LkpUserRole)


@router.get("/nivel-carrera", response_model=list[NivelCarreraResponse])
async def list_nivel_carrera(session: SessionDep, _: AuthDep) -> list[NivelCarreraResponse]:
    return await _list_entries(session, LkpNivelCarrera)


@router.get("/nucleo-carrera", response_model=list[NucleoCarreraResponse])
async def list_nucleo_carrera(session: SessionDep, _: AuthDep) -> list[NucleoCarreraResponse]:
    return await _list_entries(session, LkpNucleoCarrera)
