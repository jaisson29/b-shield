"""
B-Shield Alert System — Router: Alertas
Solo enruta y delega. Toda la lógica está en alerts_service.
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_alert_service
from app.middleware.auth import get_current_user
from app.routes.dtos.alerts_dtos import AlertCreate, AlertStatusUpdate
from app.services.alerts_service import AlertService

router = APIRouter(prefix="/v1/alerts", tags=["Alertas"])


@router.get("", summary="Listar alertas con filtros opcionales")
def list_alerts(
    _user: Annotated[dict, Depends(get_current_user)],
    alert_service: Annotated[AlertService, Depends(get_alert_service)],
    company_id: Annotated[
        int | None, Query(description="ID de la empresa")
    ] = None,
    level: Annotated[
        str | None, Query(description="critical | high | medium | low")
    ] = None,
    status: Annotated[
        str | None,
        Query(description="pending | reviewed | mitigated | ignored | in_progress"),
    ] = None,
    since: Annotated[
        str | None, Query(description="Fecha ISO mínima de emisión")
    ] = None,
):
    return alert_service.list_alerts(company_id, level, status, since)


@router.get(
    "/stats/{company_id}", summary="Dashboard: estadísticas de alertas por empresa"
)
def get_stats(
    company_id: int | None,
    _user: Annotated[dict, Depends(get_current_user)],
    alert_service: Annotated[AlertService, Depends(get_alert_service)],
):
    if not company_id or company_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paramtetro invalido",
        )

    print(
        f"company_id: {company_id} - User: {_user['sub']} - Endpoint: /v1/alerts/stats/{company_id}"
    )
    return alert_service.get_stats(company_id)


@router.get("/{alert_id}", summary="Detalle completo de una alerta")
def get_alert(
    alert_id: int,
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
    return alert_service.update_status(alert_id, body.status)
