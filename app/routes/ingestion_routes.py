from typing import Annotated

from fastapi import APIRouter, Depends

from app.store import store
from app.dependencies import get_ingestion_service

from app.middleware.auth import require_admin
from app.services.ingestions_service import IngestionsService

router = APIRouter(prefix="/v1/ingestion", tags=["Ingesta"])


@router.post("/trigger", summary="Ejecutar ciclo completo de ingesta Pipe And Filter")
async def trigger_ingestion(
    ingestion_service: Annotated[IngestionsService, Depends(get_ingestion_service)],
):

    result = await ingestion_service.run_ingestion()
    return {"message": "Ciclo de ingesta completado", "result": result}


@router.get("/status", summary="Estado del último ciclo de ingesta")
def status(_user: Annotated[dict, Depends(require_admin)]):
    return store.last_ingestion_status


@router.get("/logs", summary="Historial de ciclos de ingesta")
def logs(_user: Annotated[dict, Depends(require_admin)]):
    return {
        "total": len(store.ingestion_logs),
        "logs": store.ingestion_logs,
    }
