import uuid
from typing import Annotated

from db.models.alumno_carrera import AlumnoCarrera
from db.models.cursada import Cursada
from db.models.plan_de_estudio import PlanDeEstudio
from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import DirectorOrAdminRole
from app.schemas.common import PaginatedResponse
from app.schemas.workspace import (
    AlumnoRef,
    AlumnoRowResponse,
    CarreraInfo,
    CarreraRef,
    CursadaRowResponse,
    EstudianteDetalleResponse,
    MateriaRef,
    MateriaRowResponse,
    PlanInfo,
)
from app.services.workspace_studio import WorkspaceStudioService

router = APIRouter()

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
            carreras=[_carrera_info(ac) for ac in a.carreras],
        )
        for a in alumnos
    ]
    return PaginatedResponse(total=total, items=items)


@router.get(
    "/estudiantes/{alumno_id}",
    response_model=EstudianteDetalleResponse,
    dependencies=[DirectorOrAdminRole],
)
async def get_estudiante(alumno_id: uuid.UUID, service: ServiceDep):
    alumno, cursadas = await service.get_estudiante_detalle(alumno_id)
    return EstudianteDetalleResponse(
        id=alumno.id,
        nombre=alumno.nombre,
        apellido=alumno.apellido,
        dni=alumno.dni,
        legajo=alumno.legajo,
        carreras=[_carrera_info(ac) for ac in alumno.carreras],
        cursadas=[_cursada_row(c) for c in cursadas],
    )


@router.get(
    "/cursadas",
    response_model=PaginatedResponse[CursadaRowResponse],
    dependencies=[DirectorOrAdminRole],
)
async def list_cursadas(
    service: ServiceDep,
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    carrera_id: uuid.UUID | None = None,
    alumno: str | None = None,
    materia: str | None = None,
    anio: int | None = None,
    cuatrimestre: str | None = None,
    estado_cursada: Annotated[list[str] | None, Query()] = None,
    tipo_cursada: str | None = None,
):
    total, cursadas = await service.list_cursadas(
        skip=skip,
        limit=limit,
        carrera_id=carrera_id,
        alumno=alumno,
        materia=materia,
        anio=anio,
        cuatrimestre=cuatrimestre,
        estado_cursada=estado_cursada,
        tipo_cursada=tipo_cursada,
    )
    return PaginatedResponse(total=total, items=[_cursada_row(c) for c in cursadas])


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


def _carrera_info(ac: AlumnoCarrera) -> CarreraInfo:
    return CarreraInfo(
        plan_id=ac.plan_id,
        plan_nombre=ac.plan.nombre,
        anio=ac.plan.anio,
        vigente=ac.plan.vigente,
        carrera_id=ac.plan.carrera.id,
        carrera_nombre=ac.plan.carrera.nombre,
        estado_academico=ac.estado_academico,
        fecha_ingreso=ac.fecha_ingreso,
    )


def _plan_info(p: PlanDeEstudio) -> PlanInfo:
    return PlanInfo(
        plan_id=p.id,
        plan_nombre=p.nombre,
        anio=p.anio,
        vigente=p.vigente,
        carrera_id=p.carrera.id,
        carrera_nombre=p.carrera.nombre,
    )


def _cursada_row(c: Cursada) -> CursadaRowResponse:
    return CursadaRowResponse(
        id=c.id,
        alumno=AlumnoRef(id=c.alumno.id, nombre=c.alumno.nombre, apellido=c.alumno.apellido, legajo=c.alumno.legajo),
        materia=MateriaRef(id=c.materia.id, codigo=c.materia.codigo, nombre=c.materia.nombre),
        carrera=CarreraRef(id=c.carrera.id, codigo=c.carrera.codigo, nombre=c.carrera.nombre),
        anio=c.anio,
        cuatrimestre=c.cuatrimestre,
        comision=c.comision,
        tipo_cursada=c.tipo_cursada,
        estado_cursada=c.estado_cursada,
        nota=c.nota,
    )
