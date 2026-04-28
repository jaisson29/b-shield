from typing import Awaitable, Callable

from fastapi import HTTPException, Request, Response

from app.services.auth_service import AuthService

PUBLIC_PATHS = {"/login", "/health", "/docs", "/openapi.json", "/redoc"}

VALID_TOKENS: dict[str, dict] = {
    "bshield-admin-token": {
        "sub": "user-001",
        "rol": "admin",
        "nombre": "Admin B-Shield",
    },
    "bshield-consultor-token": {
        "sub": "user-002",
        "rol": "consultor",
        "nombre": "Consultor Demo",
    },
    "bshield-demo-token": {"sub": "user-003", "rol": "admin", "nombre": "Demo User"},
}

auth_service = AuthService()


async def auth_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
):
    """Middleware global de autenticación Bearer."""
    path = f"/{request.url.path.rsplit("/", 1)[-1]}"

    if path in PUBLIC_PATHS or path.endswith("/docs") or path.endswith("/redoc"):
        return await call_next(request)

    auth_header = request.headers.get("authorization", "")

    if not auth_header.startswith("Bearer "):
        return Response(
            content="Se requiere Authorization: Bearer <token>.",
            status_code=401,
        )
    token = auth_header.split(" ", 1)[1]
    if token in VALID_TOKENS:
        request.state.user = VALID_TOKENS[token]
        return await call_next(request)

    user = auth_service.decode_token(token)
    request.state.user = user
    return await call_next(request)


def get_current_user(request: Request) -> dict:
    """Dependency: obtiene el usuario autenticado de la request."""
    return getattr(
        request.state,
        "user",
        {"sub": "unknown", "rol": "consultor", "nombre": "Unknown"},
    )


def require_admin(request: Request) -> dict:
    """Dependency: exige rol admin."""
    user = get_current_user(request)
    if user.get("rol") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Esta operacion requiere rol de administrador.",
        )
    return user
