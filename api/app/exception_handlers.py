from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.errors import AcademikaError, BusinessError, ConflictError, ForbiddenError, NotFoundError, UnauthorizedError


def add_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotFoundError, not_found_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ConflictError, conflict_handler)  # type: ignore[arg-type]
    app.add_exception_handler(BusinessError, business_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(UnauthorizedError, unauthorized_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ForbiddenError, forbidden_handler)  # type: ignore[arg-type]
    app.add_exception_handler(AcademikaError, academika_error_handler)  # type: ignore[arg-type]


async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.detail})


async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": exc.detail})


async def business_error_handler(request: Request, exc: BusinessError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.detail})


async def unauthorized_handler(request: Request, exc: UnauthorizedError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": exc.detail})


async def forbidden_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": exc.detail})


async def academika_error_handler(request: Request, exc: AcademikaError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": exc.detail})
