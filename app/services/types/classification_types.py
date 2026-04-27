from pydantic import BaseModel, Field


class EvaluateCommand(BaseModel):
    company_id: str
    cwe_id: str
    cvss_score: float = Field(ge=0, le=10)
    affected_technologies: list[str] = []
