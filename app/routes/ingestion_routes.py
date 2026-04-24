from fastapi import APIRouter

from app.store import Store


router = APIRouter(prefix="/v1/ingestion", tags=["Ingesta"])


@router.post("/trigger", summary="Ejecutar ciclo completo de ingesta Pipe And Filter")
async def trigger_ingestion():
    from app.services.ingestions_service import IngestionsService

    db = Store()
    ingestion_service = IngestionsService(db)
    result = await ingestion_service.run_ingestion()
    return {"message": "Ciclo de ingesta completado", "result": result}
