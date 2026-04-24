from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.routes import ingestion_routes
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="B-Shield Alert System API",
    description=(
        "Sistema de Inteligencia Preventiva de Seguridad para PyMEs Tecnológicas.\n\n"
        "**Arquitectura:** SOA · **Patrón central:** Pipe & Filter · **Backend:** Python/FastAPI\n\n"
        "**Token de prueba:** `bshield-demo-token`"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(BaseHTTPMiddleware, dispatch=auth_middleware)


router = APIRouter(prefix="/api")

router.include_router(ingestion_routes.router)

@router.get("/health", tags=["Sistema"], summary="Estado del servicio")
def health_check():
    from datetime import datetime, timezone

    return {
        "status": "ok",
        "service": "b-shield-alert-system",
        "version": "1.0.0",
        "backend": "Python / FastAPI",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

app.include_router(router)
