"""
B-Shield Alert System — Almacén de datos en memoria
En producción reemplazar por SQLAlchemy + PostgreSQL
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel


# ── Modelos Pydantic ──────────────────────────────────────────
class Company(BaseModel):
    id: str
    nombre: str
    sector: str
    tamano: str
    pais: str
    stack: list[str]
    umbral_cvss: float
    contacto_email: Optional[str]
    creado_en: str
    actualizado_en: Optional[str] = None


class Alert(BaseModel):
    id: str
    empresa_id: str
    cwe_id: str
    cwe_nombre: str
    cvss_score: float
    irc_score: float
    nivel_criticidad: str
    tecnologias_afectadas: list[str]
    descripcion: str
    recomendacion: str
    fuente_url: Optional[str]
    estado: str
    fecha_emision: str
    fecha_actualizacion: Optional[str]


class IngestionLog(BaseModel):
    estado: str
    inicio: Optional[str]
    fin: Optional[str]
    reportes_recibidos: int
    alertas_generadas: int
    error: Optional[str]


# ── Singleton del store ───────────────────────────────────────
class Store:
    def __init__(self):

        self._alert_counter = 4
        self._company_counter = 3

        self.companies: dict[str, dict] = {
            "emp-001": {
                "id": "emp-001",
                "nombre": "TechPyME SAS",
                "sector": "fintech",
                "tamano": "pequena",
                "pais": "Colombia",
                "stack": ["node.js", "express", "mongodb", "aws", "docker"],
                "umbral_cvss": 6.0,
                "contacto_email": "sysadmin@techpyme.co",
                "creado_en": "2026-01-15T00:00:00Z",
                "actualizado_en": None,
            },
            "emp-002": {
                "id": "emp-002",
                "nombre": "DataSoft Ltda",
                "sector": "edtech",
                "tamano": "mediana",
                "pais": "Colombia",
                "stack": ["python", "django", "postgresql", "gcp", "react"],
                "umbral_cvss": 7.0,
                "contacto_email": "it@datasoft.co",
                "creado_en": "2026-02-01T00:00:00Z",
                "actualizado_en": None,
            },
        }

        self.alerts: list[dict] = [
            {
                "id": "alert-0001",
                "empresa_id": "emp-001",
                "cwe_id": "CWE-89",
                "cwe_nombre": "SQL/NoSQL Injection",
                "cvss_score": 9.1,
                "irc_score": 8.86,
                "nivel_criticidad": "Critico",
                "tecnologias_afectadas": ["mongodb", "node.js"],
                "descripcion": "Vulnerabilidad de inyeccion en driver de MongoDB que permite acceso no autorizado a datos.",
                "recomendacion": "Actualizar mongodb driver >= 5.9.2. Validar entradas con Pydantic.",
                "fuente_url": "https://hackerone.com/reports/demo-001",
                "estado": "Pendiente",
                "fecha_emision": "2026-04-08T00:00:00Z",
                "fecha_actualizacion": None,
            },
            {
                "id": "alert-0002",
                "empresa_id": "emp-001",
                "cwe_id": "CWE-79",
                "cwe_nombre": "Cross-Site Scripting (XSS)",
                "cvss_score": 6.5,
                "irc_score": 6.8,
                "nivel_criticidad": "Alto",
                "tecnologias_afectadas": ["express", "node.js"],
                "descripcion": "Fallo de sanitizacion en respuestas JSON que permite inyeccion de scripts.",
                "recomendacion": "Implementar CSP. Configurar headers de seguridad en FastAPI con middleware.",
                "fuente_url": "https://hackerone.com/reports/demo-002",
                "estado": "Revisada",
                "fecha_emision": "2026-04-05T00:00:00Z",
                "fecha_actualizacion": "2026-04-06T00:00:00Z",
            },
            {
                "id": "alert-0003",
                "empresa_id": "emp-002",
                "cwe_id": "CWE-306",
                "cwe_nombre": "Missing Authentication",
                "cvss_score": 7.8,
                "irc_score": 7.2,
                "nivel_criticidad": "Alto",
                "tecnologias_afectadas": ["django", "postgresql"],
                "descripcion": "Endpoint de administracion Django expuesto sin autenticacion en configuracion por defecto.",
                "recomendacion": "Revisar settings.py, deshabilitar DEBUG en produccion, proteger /admin con 2FA.",
                "fuente_url": "https://hackerone.com/reports/demo-003",
                "estado": "Mitigada",
                "fecha_emision": "2026-04-01T00:00:00Z",
                "fecha_actualizacion": "2026-04-03T00:00:00Z",
            },
        ]

        self.ingestion_logs: list[dict] = []
        self.last_ingestion_status: dict = {
            "estado": "nunca_ejecutado",
            "inicio": None,
            "fin": None,
            "reportes_recibidos": 0,
            "alertas_generadas": 0,
            "error": None,
        }

    def next_alert_id(self) -> str:
        aid = f"alert-{self._alert_counter:04d}"
        self._alert_counter += 1
        return aid

    def next_company_id(self) -> str:
        cid = f"emp-{self._company_counter:03d}"
        self._company_counter += 1
        return cid


store = Store()
