"""
B-Shield Alert System — Router: Clasificación
Solo enruta y delega. Toda la lógica está en classification_service.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_classification_service
from app.middleware.auth import get_current_user
from app.routes.dtos.classification_dtos import EvaluateRequest
from app.services.classifcation_service import ClassificationService
from app.services.types.classification_types import EvaluateCommand

router = APIRouter(prefix="/v1/classification", tags=["Clasificacion"])


@router.post(
    "/evaluate", summary="Evaluar criticidad de una vulnerabilidad para una empresa"
)
def evaluate(
    body: EvaluateRequest,
    _user: Annotated[dict, Depends(get_current_user)],
    classification_service: Annotated[
        ClassificationService, Depends(get_classification_service)
    ],
):
    mapped_body = EvaluateCommand(**body.model_dump())

    return classification_service.evaluate(mapped_body)


@router.get("/catalog", summary="Catálogo de CWEs soportados con mitigaciones OWASP")
def catalog(
    _user: Annotated[dict, Depends(get_current_user)],
    classification_service: Annotated[
        ClassificationService, Depends(get_classification_service)
    ],
):
    return classification_service.get_catalog()
