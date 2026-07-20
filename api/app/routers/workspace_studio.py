import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import require_role
from app.models.plan_de_estudio import PlanDeEstudio
from app.schemas.common import PaginatedResponse
from app.schemas.workspace import AlumnoRowResponse, MateriaRowResponse, PlanInfo, _CarreraInfo
from app.services.workspace_studio import WorkspaceStudioService

router = APIRouter()

DirectorOrAdminRole = Depends(require_role("director", "admin"))
ServiceDep = Annotated[WorkspaceStudioService, Depends(WorkspaceStudioService.dep)]


@router.get(
    "/estudiantes",
    response_model=PaginatedResponse[AlumnoRowResponse],
    dependencies=[DirectorOrAdminRole],
)
async def list_estudiantes(
    service: ServiceDep,
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    carrera_id: uuid.UUID | None = None,
    estado_academico: str | None = None,
):
    total, alumnos = await service.list_estudiantes(
        skip=skip,
        limit=limit,
        carrera_id=carrera_id,
        estado_academico=estado_academico,
    )
    items = [
        AlumnoRowResponse(
            id=a.id,
            nombre=a.nombre,
            apellido=a.apellido,
            dni=a.dni,
            legajo=a.legajo,
            carreras=[
                _CarreraInfo(
                    plan_id=ac.plan_id,
                    plan_nombre=ac.plan.nombre,
                    anio=ac.plan.anio,
                    vigente=ac.plan.vigente,
                    carrera_id=ac.plan.carrera.id,
                    carrera_nombre=ac.plan.carrera.nombre,
                    estado_academico=ac.estado_academico,
                    fecha_ingreso=ac.fecha_ingreso,
                )
                for ac in a.carreras
            ],
        )
        for a in alumnos
    ]
    return PaginatedResponse(total=total, items=items)


@router.get(
    "/materias",
    response_model=PaginatedResponse[MateriaRowResponse],
    dependencies=[DirectorOrAdminRole],
)
async def list_materias(
    service: ServiceDep,
    skip: int = 0,
    limit: int = Query(default=20, le=100),
):
    total, materias = await service.list_materias(skip=skip, limit=limit)
    items = [
        MateriaRowResponse(
            id=m.id,
            nombre=m.nombre,
            codigo=m.codigo,
            sigla=m.sigla,
            creditos=m.creditos,
            plan_vigente=next(
                (_plan_info(p) for p in sorted(m.planes, key=lambda p: p.anio, reverse=True) if p.vigente),
                None,
            ),
            planes=[_plan_info(p) for p in m.planes],
        )
        for m in materias
    ]
    return PaginatedResponse(total=total, items=items)


def _plan_info(p: PlanDeEstudio) -> PlanInfo:
    return PlanInfo(
        plan_id=p.id,
        plan_nombre=p.nombre,
        anio=p.anio,
        vigente=p.vigente,
        carrera_id=p.carrera.id,
        carrera_nombre=p.carrera.nombre,
    )
