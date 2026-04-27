from typing import Annotated
from fastapi import APIRouter, Depends

from app.models.company import Company
from app.routes.dtos.companies_dtos import CompanyCreate, StackUpdate
from app.services.companies_service import CompanyService
from app.store import store
from app.dependencies import get_company_service, get_ingestion_service

from app.middleware.auth import get_current_user, require_admin
from app.services.ingestions_service import IngestionsService

router = APIRouter(prefix="/v1/companies", tags=["Empresas"])


@router.get("", summary="Listar todas las empresas registradas (admin)")
def list_companies(
    _user: Annotated[dict, Depends(require_admin)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
):
    return company_service.list_companies()


@router.post(
    "", status_code=201, summary="Registrar nueva empresa con perfil tecnológico"
)
def create_company(
    body: CompanyCreate,
    _user: Annotated[dict, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
):
    mapped_body = Company(**body.model_dump())
    return company_service.create_company(mapped_body)


@router.get(
    "/{empresa_id}/profile", summary="Obtener perfil tecnológico de una empresa"
)
def get_profile(
    empresa_id: int,
    _user: Annotated[dict, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
):
    return company_service.get_profile(empresa_id)


@router.put("/{empresa_id}/stack", summary="Actualizar stack tecnológico")
def update_stack(
    empresa_id: int,
    body: StackUpdate,
    _user: Annotated[dict, Depends(get_current_user)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
):
    return company_service.update_stack(empresa_id, body)


@router.delete("/{empresa_id}", summary="Eliminar empresa (admin)")
def delete_company(
    empresa_id: int,
    _user: Annotated[dict, Depends(require_admin)],
    company_service: Annotated[CompanyService, Depends(get_company_service)],
):
    return company_service.delete_company(empresa_id)
