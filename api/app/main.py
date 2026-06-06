from fastapi import FastAPI

from app.exception_handlers import add_error_handlers
from app.routers import (
    auth,
    course_enrollments,
    courses,
    degrees,
    health,
    lookups,
    students,
    study_plans,
)

app = FastAPI(title="Académika API")

add_error_handlers(app)

app.include_router(health.router, prefix="/health", tags=["health"])

api_prefix = "/api/v1"

app.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["auth"])

app.include_router(degrees.router, prefix=f"{api_prefix}/carreras", tags=["carreras"])
app.include_router(courses.router, prefix=f"{api_prefix}/materias", tags=["materias"])
app.include_router(study_plans.router, prefix=f"{api_prefix}/planes", tags=["planes"])
app.include_router(students.router, prefix=f"{api_prefix}/alumnos", tags=["alumnos"])
app.include_router(
    course_enrollments.router,
    prefix=f"{api_prefix}/inscripciones",
    tags=["inscripciones"],
)
app.include_router(lookups.router, prefix=f"{api_prefix}/lookups", tags=["lookups"])
