from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_auth_service

from app.routes.dtos.auth_dtos import AuthLoginDTO
from app.services.auth_service import AuthService

router = APIRouter(prefix="/v1/auth", tags=["Autenticación"])


@router.post("/login", summary="Ejecutar ciclo completo de ingesta Pipe And Filter")
def login(
    user: AuthLoginDTO,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    demo_users = {
        "admin": {"username": "admin", "password": "admin123", "rol": "admin"},
        "consultor": {"username": "consultor", "password": "consultor123", "rol": "consultor"},
    }
    # Simular autenticación (en producción, validar contra base de datos)
    found_user = demo_users.get(user.username)
    if not found_user:
        raise ValueError("Credenciales invalidas")

    if user.password != found_user["password"]:
        raise ValueError("Credenciales invalidas")

    user_info = {
        "sub": f"user-{found_user['username']}",
        "rol": found_user.get("rol"),
        "nombre": f"{found_user['username'].title()} B-Shield",
    }
    result = auth_service.generate_token(user_info)
    return result
