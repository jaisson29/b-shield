from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_ingestion_service
from app.store import Store

from app.services.ingestions_service import IngestionsService

router = APIRouter(prefix="/v1/ingestion", tags=["Ingesta"])


@router.post("/trigger", summary="Ejecutar ciclo completo de ingesta Pipe And Filter")
async def trigger_ingestion(
    ingestion_service: Annotated[IngestionsService, Depends(get_ingestion_service)],
):

    result = await ingestion_service.run_ingestion()
    return {"message": "Ciclo de ingesta completado", "result": result}
