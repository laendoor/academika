from fastapi import APIRouter
from sqlalchemy import select

from app.db.session import SessionDep
from app.errors import NotFoundError
from app.models.lkp_estado_academico import LkpEstadoAcademico
from app.models.lkp_estado_cursada import LkpEstadoCursada
from app.models.lkp_tipo_cursada import LkpTipoCursada
from app.schemas.lookups import EstadoAcademicoResponse, EstadoCursadaResponse, TipoCursadaResponse

router = APIRouter()


@router.get("/estado-academico", response_model=list[EstadoAcademicoResponse])
async def list_estado_academico(session: SessionDep) -> list[LkpEstadoAcademico]:
    result = await session.execute(select(LkpEstadoAcademico))
    return list(result.scalars().all())


@router.get("/estado-academico/{key}", response_model=EstadoAcademicoResponse)
async def get_estado_academico(key: str, session: SessionDep) -> LkpEstadoAcademico:
    instance = await session.get(LkpEstadoAcademico, key)
    if instance is None:
        raise NotFoundError("estado_academico", key)
    return instance


@router.get("/estado-cursada", response_model=list[EstadoCursadaResponse])
async def list_estado_cursada(session: SessionDep) -> list[LkpEstadoCursada]:
    result = await session.execute(select(LkpEstadoCursada))
    return list(result.scalars().all())


@router.get("/estado-cursada/{key}", response_model=EstadoCursadaResponse)
async def get_estado_cursada(key: str, session: SessionDep) -> LkpEstadoCursada:
    instance = await session.get(LkpEstadoCursada, key)
    if instance is None:
        raise NotFoundError("estado_cursada", key)
    return instance


@router.get("/tipo-cursada", response_model=list[TipoCursadaResponse])
async def list_tipo_cursada(session: SessionDep) -> list[LkpTipoCursada]:
    result = await session.execute(select(LkpTipoCursada))
    return list(result.scalars().all())


@router.get("/tipo-cursada/{key}", response_model=TipoCursadaResponse)
async def get_tipo_cursada(key: str, session: SessionDep) -> LkpTipoCursada:
    instance = await session.get(LkpTipoCursada, key)
    if instance is None:
        raise NotFoundError("tipo_cursada", key)
    return instance
