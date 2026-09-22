from fastapi.routing import APIRoute

from app.auth.dependencies import get_current_user
from app.main import app

PUBLIC_PATHS = {
    "/health",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/auth/forgot-password",
    "/api/v1/auth/reset-password",
}


def _requires_auth(route: APIRoute) -> bool:
    def walk(dependant) -> bool:
        if dependant.call is get_current_user:
            return True
        return any(walk(sub) for sub in dependant.dependencies)

    return walk(route.dependant)


def test_routes_require_auth_except_whitelist() -> None:
    unprotected = sorted(
        route.path
        for route in app.routes
        if isinstance(route, APIRoute) and route.path not in PUBLIC_PATHS and not _requires_auth(route)
    )

    assert not unprotected, f"rutas sin auth fuera de la whitelist de públicas: {unprotected}"
