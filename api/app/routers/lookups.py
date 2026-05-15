from fastapi import APIRouter
from sqlalchemy import select

from app.db.session import SessionDep
from app.errors import NotFoundError
from app.models.lkp_academic_status import LkpAcademicStatus
from app.models.lkp_enrollment_status import LkpEnrollmentStatus
from app.models.lkp_enrollment_type import LkpEnrollmentType
from app.schemas.lookups import AcademicStatusResponse, EnrollmentStatusResponse, EnrollmentTypeResponse

router = APIRouter()


@router.get("/academic-status", response_model=list[AcademicStatusResponse])
async def list_academic_status(session: SessionDep) -> list[LkpAcademicStatus]:
    result = await session.execute(select(LkpAcademicStatus))
    return list(result.scalars().all())


@router.get("/academic-status/{key}", response_model=AcademicStatusResponse)
async def get_academic_status(key: str, session: SessionDep) -> LkpAcademicStatus:
    instance = await session.get(LkpAcademicStatus, key)
    if instance is None:
        raise NotFoundError("academic_status", key)
    return instance


@router.get("/enrollment-status", response_model=list[EnrollmentStatusResponse])
async def list_enrollment_status(session: SessionDep) -> list[LkpEnrollmentStatus]:
    result = await session.execute(select(LkpEnrollmentStatus))
    return list(result.scalars().all())


@router.get("/enrollment-status/{key}", response_model=EnrollmentStatusResponse)
async def get_enrollment_status(key: str, session: SessionDep) -> LkpEnrollmentStatus:
    instance = await session.get(LkpEnrollmentStatus, key)
    if instance is None:
        raise NotFoundError("enrollment_status", key)
    return instance


@router.get("/enrollment-type", response_model=list[EnrollmentTypeResponse])
async def list_enrollment_type(session: SessionDep) -> list[LkpEnrollmentType]:
    result = await session.execute(select(LkpEnrollmentType))
    return list(result.scalars().all())


@router.get("/enrollment-type/{key}", response_model=EnrollmentTypeResponse)
async def get_enrollment_type(key: str, session: SessionDep) -> LkpEnrollmentType:
    instance = await session.get(LkpEnrollmentType, key)
    if instance is None:
        raise NotFoundError("enrollment_type", key)
    return instance
