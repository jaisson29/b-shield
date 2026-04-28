from pydantic import BaseModel, Field
from typing import Optional

from app.store import Alert


# ── Alertas ───────────────────────────────────────────────────
class AlertCreate(BaseModel):
    empresa_id: str
    cwe_id: str
    cwe_nombre: Optional[str] = None
    cvss_score: float = Field(ge=0, le=10)
    irc_score: float
    nivel_criticidad: str
    tecnologias_afectadas: list[str] = []
    descripcion: str
    recomendacion: str
    fuente_url: Optional[str] = None


class AlertStatusUpdate(BaseModel):
    status: str

class AlertsResponse(BaseModel):
    total: int
    filtros: dict
    alerts: list[Alert]
