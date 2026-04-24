from pydantic import BaseModel, Field
from typing import Optional


# ── Empresas ──────────────────────────────────────────────────
class CompanyCreate(BaseModel):
    nombre: str
    sector: str
    stack: list[str]
    tamano: Optional[str] = "no especificado"
    pais: Optional[str] = "Colombia"
    umbral_cvss: Optional[float] = 7.0
    contacto_email: Optional[str] = None


class StackUpdate(BaseModel):
    stack: list[str]
    umbral_cvss: Optional[float] = None
