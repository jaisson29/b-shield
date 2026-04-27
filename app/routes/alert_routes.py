"""
B-Shield Alert System — Router: Alertas
Solo enruta y delega. Toda la lógica está en alerts_service.
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query

from app.dependencies import get_alert_service
from app.middleware.auth import get_current_user
from app.routes.dtos.alerts_dtos import AlertCreate, AlertStatusUpdate
from app.services.alerts_service import AlertService

router = APIRouter(prefix="/v1/alerts", tags=["Alertas"])


@router.get("", summary="Listar alertas con filtros opcionales")
def list_alerts(
    _user: Annotated[dict, Depends(get_current_user)],
    alert_service: Annotated[AlertService, Depends(get_alert_service)],
    company_id: Annotated[int, Query(min_value=1, description="ID de la empresa")],
    nivel: Annotated[
        str | None, Query(description="Critico | Alto | Medio | Bajo")
    ] = None,
    estado: Annotated[
        str | None,
        Query(description="Pendiente | Revisada | Mitigada | Ignorada | En proceso"),
    ] = None,
    desde: Annotated[
        str | None, Query(description="Fecha ISO mínima de emisión")
    ] = None,
):
    return alert_service.list_alerts(company_id, nivel, estado, desde)


@router.get(
    "/stats/{company_id}", summary="Dashboard: estadísticas de alertas por empresa"
)
def get_stats(
    company_id: int,
    _user: Annotated[dict, Depends(get_current_user)],
    alert_service: Annotated[AlertService, Depends(get_alert_service)],
):
    return alert_service.get_stats(company_id)


@router.get("/{alert_id}", summary="Detalle completo de una alerta")
def get_alert(
    alert_id: str,
    _user: Annotated[dict, Depends(get_current_user)],
    alert_service: Annotated[AlertService, Depends(get_alert_service)],
):
    return alert_service.get_alert(alert_id)


@router.post(
    "", status_code=201, summary="Crear alerta manualmente (uso interno del pipeline)"
)
def create_alert(
    body: AlertCreate,
    _user: Annotated[dict, Depends(get_current_user)],
    alert_service: Annotated[AlertService, Depends(get_alert_service)],
):
    return alert_service.create_alert(body)


@router.patch(
    "/{alert_id}/status", summary="Actualizar estado de gestión de una alerta"
)
def update_status(
    alert_id: int,
    body: AlertStatusUpdate,
    user: Annotated[dict, Depends(get_current_user)],
    alert_service: Annotated[AlertService, Depends(get_alert_service)],
):
    return alert_service.update_status(alert_id, body.status, user["sub"])
