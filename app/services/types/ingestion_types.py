from pydantic import BaseModel

class RawReportAttributes(BaseModel):
    title: str
    url: str
    substate: str
    cwe_id: str | None
    weakness: str | None
    severity_score: float | None
    severity_rating: str
    created_at: str
    disclosed_at: str | None
    severity: dict | None

class RawReport(BaseModel):
    id: int
    type: str
    attributes: RawReportAttributes
    relationships: dict

class NormalizedReport(BaseModel):
    fuente_id: int
    cwe_id: str
    cvss_score: float
    titulo: str
    fecha: str
    fuente_url: str
    tecnologias_detectadas: list[str]

class RelevancyReport(NormalizedReport):
    empresa_id: str
    empresa_nombre: str
    impactadas: list[str]

class ClassifiedReport(RelevancyReport):
    irc_score: float
    nivel_criticidad: str
    
class ReportDetailedAttributes(BaseModel):
    title: str
    state: str
    created_at: str
    closed_at: str | None
    disclosed_at: str | None


class ReportDetailedSeverity(BaseModel):
    scope: str
    score: float
    rating: str


class ReportDetailedWeakness(BaseModel):

    name: str
    description: str
    external_id: str | None
    created_at: str


class ReportDetailed(BaseModel):
    id: int
    type: str
    attributes: ReportDetailedAttributes | None
    severity: ReportDetailedSeverity | None
    weakness: ReportDetailedWeakness | None
