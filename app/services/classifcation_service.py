from datetime import datetime, timezone
from fastapi import HTTPException

from app.repositories.alert_repository import AlertRepository
from app.repositories.company_repository import CompanyRepository
from app.services.types.classification_types import EvaluateCommand


class ClassificationService:
    MITIGACIONES: dict[str, dict] = {
        "CWE-89": {
            "nombre": "SQL/NoSQL Injection",
            "owasp": "A03:2021",
            "recomendacion": "Usar consultas parametrizadas. Nunca concatenar entradas del usuario en queries.",
        },
        "CWE-79": {
            "nombre": "Cross-Site Scripting (XSS)",
            "owasp": "A03:2021",
            "recomendacion": "Sanitizar salidas. Implementar CSP. Configurar headers de seguridad en FastAPI.",
        },
        "CWE-306": {
            "nombre": "Missing Authentication",
            "owasp": "A07:2021",
            "recomendacion": "Proteger todos los endpoints con autenticacion. Revisar configuracion por defecto.",
        },
        "CWE-22": {
            "nombre": "Path Traversal",
            "owasp": "A01:2021",
            "recomendacion": "Validar rutas con os.path.realpath(). Usar whitelist de directorios permitidos.",
        },
        "CWE-502": {
            "nombre": "Insecure Deserialization",
            "owasp": "A08:2021",
            "recomendacion": "Evitar pickle con datos no confiables. Usar Pydantic para validacion de entradas.",
        },
        "CWE-287": {
            "nombre": "Improper Authentication",
            "owasp": "A07:2021",
            "recomendacion": "Implementar autenticacion multifactor. Validar tokens con python-jose.",
        },
        "CWE-200": {
            "nombre": "Information Exposure",
            "owasp": "A02:2021",
            "recomendacion": "No exponer datos sensibles en logs. Usar exception handlers globales en FastAPI.",
        },
        "CWE-798": {
            "nombre": "Hard-coded Credentials",
            "owasp": "A02:2021",
            "recomendacion": "Usar variables de entorno con python-dotenv. Nunca hardcodear credenciales.",
        },
        "CWE-434": {
            "nombre": "Unrestricted File Upload",
            "owasp": "A04:2021",
            "recomendacion": "Validar tipo MIME y extension. Limitar tamaño. Almacenar fuera del webroot.",
        },
        "DEFAULT": {
            "nombre": "Vulnerabilidad General",
            "owasp": "Ver OWASP Top Ten",
            "recomendacion": "Revisar OWASP Top 10 y NVD para mitigaciones especificas del CWE.",
        },
    }

    def __init__(
        self, company_repository: CompanyRepository, alert_repository: AlertRepository
    ):
        self.company_repository = company_repository
        self.alert_repository = alert_repository

    def calculate_irc_level(self, irc: float) -> str:
        if irc >= 8.5:
            return "critical"
        if irc >= 6.5:
            return "high"
        if irc >= 4.0:
            return "medium"
        return "low"

    def evaluate(self, body: EvaluateCommand):
        empresa = self.company_repository.get_company_by_id(body.company_id)
        if not empresa:
            raise HTTPException(
                404, detail=f"Empresa '{body.company_id}' no encontrada"
            )

        tech_afect = [t.lower() for t in body.affected_technologies]
        stack_emp = [t.lower() for t in empresa.stack]

        impactadas = (
            [t for t in tech_afect if t in stack_emp] if tech_afect else stack_emp
        )
        exposicion = len(impactadas) / len(stack_emp) if stack_emp else 0.0

        irc_score = round(body.cvss_score * 0.6 + exposicion * 10 * 0.4, 2)
        nivel = self.calculate_irc_level(irc_score)
        mit = self.MITIGACIONES.get(body.cwe_id, self.MITIGACIONES["DEFAULT"])

        return {
            "company_id": body.company_id,
            "empresa_nombre": empresa.name,
            "cwe_id": body.cwe_id,
            "cwe_nombre": mit["nombre"],
            "cvss_score": body.cvss_score,
            "exposicion_stack": round(exposicion * 100, 1),
            "irc_score": irc_score,
            "nivel_criticidad": nivel,
            "supera_umbral_empresa": body.cvss_score >= empresa.threshold_cvss,
            "tecnologias_impactadas": impactadas,
            "tecnologias_no_afectadas": [t for t in stack_emp if t not in impactadas],
            "mitigacion": {
                "owasp": mit["owasp"],
                "recomendacion": mit["recomendacion"],
            },
            "evaluado_en": datetime.now(timezone.utc).isoformat(),
        }

    def get_catalog(self) -> dict:
        cwes = [
            {"cwe_id": k, **v} for k, v in self.MITIGACIONES.items() if k != "DEFAULT"
        ]
        return {"total": len(cwes), "cwes": cwes}

    def get_mitigation(self, cwe_id: str) -> dict:
        """Util usado internamente por el pipeline de ingesta."""
        return self.MITIGACIONES.get(cwe_id, self.MITIGACIONES["DEFAULT"])
