# ── Clasificacion ─────────────────────────────────────────────
from pydantic import BaseModel, Field


class EvaluateRequest(BaseModel):
    company_id: str
    cwe_id: str
    cvss_score: float = Field(ge=0, le=10)
    affected_technologies: list[str] = []
