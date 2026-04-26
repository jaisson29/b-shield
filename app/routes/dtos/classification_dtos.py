# # ── Clasificacion ─────────────────────────────────────────────
# from pydantic import BaseModel, Field


# class EvaluateRequest(BaseModel):
#     empresa_id: str
#     cwe_id: str
#     cvss_score: float = Field(ge=0, le=10)
#     tecnologias_afectadas: list[str] = []
