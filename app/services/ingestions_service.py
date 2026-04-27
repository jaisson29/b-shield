import asyncio
from datetime import datetime, timedelta, timezone

import httpx
from app.store import store
from app.infrastructure.h1_client import (
    fetch_recent_hacktivity,
    mapear_cvss,
)
from app.models.alert import Alert
from app.repositories.alert_repository import AlertRepository
from app.repositories.company_repository import CompanyRepository
from app.services.classifcation_service import ClassificationService
from app.services.notification_service import NotificationService
from app.services.types.ingestion_types import (
    ClassifiedReport,
    NormalizedReport,
    RawReport,
    RelevancyReport,
)


class IngestionsService:
    def __init__(
        self,
        company_repository: CompanyRepository,
        alert_repository: AlertRepository,
        notification_service: NotificationService,
        classification_service: ClassificationService,
    ):
        self.company_repository = company_repository
        self.alert_repository = alert_repository
        self.notification_service = notification_service
        self.classification_service = classification_service

    TECH_MAP: dict[str, str] = {
        "node": "node.js",
        "nodejs": "node.js",
        "express": "express",
        "nestjs": "node.js",
        "fastapi": "python",
        "flask": "python",
        "django": "django",
        "python": "python",
        "mongodb": "mongodb",
        "mongo": "mongodb",
        "react": "react",
        "vue": "vue",
        "angular": "angular",
        "postgresql": "postgresql",
        "postgres": "postgresql",
        "mysql": "mysql",
        "redis": "redis",
        "aws": "aws",
        "gcp": "gcp",
        "azure": "azure",
        "docker": "docker",
        "kubernetes": "kubernetes",
        "nginx": "nginx",
        "apache": "apache",
    }

    async def run_ingestion(self):
        start = self._now()
        print(f"\n[Pipeline] ════ Inicio de ciclo: {start} ════")
        raw_data = await self.filter_1_ingestion()
        normalized_data = self.filter_2_normalization(raw_data)
        relevancy_data = self.filter_3_relevancy(normalized_data)
        classified_data = self.filter_4_clasification(relevancy_data)
        enriched_data = self.filter_5_enrichment(classified_data)
        generated = self.filter_6_distribution(enriched_data)

        end = self._now()
        status = {
            "estado": "exitoso",
            "inicio": start,
            "fin": end,
            "reportes_recibidos": len(raw_data),
            "alertas_generadas": generated,
            "error": None,
        }
        store.last_ingestion_status.update(status)
        store.ingestion_logs.append(dict(status))
        print(f"[Pipeline] ════ Completado: {generated} alerta(s) generada(s) ════\n")
        return status

    def _now(self) -> datetime:

        return datetime.now(timezone.utc)

    async def filter_1_ingestion(self) -> list[RawReport]:
        async with httpx.AsyncClient() as client:
            client.base_url = "https://api.hackerone.com/v1"

            response = await fetch_recent_hacktivity(page_size=100)
            return [RawReport(**r) for r in response]

    def filter_2_normalization(
        self, raw_data: list[RawReport]
    ) -> list[NormalizedReport]:
        print(f"[Pipeline][F2] Normalizando {len(raw_data)} reportes...")

        def extraer_techs(titulo: str) -> list[str]:
            lower = titulo.lower()
            return list({v for k, v in self.TECH_MAP.items() if k in lower})

        normalized = []

        for r in raw_data:
            normalized.append(
                NormalizedReport(
                    fuente_id=r.id,
                    cwe_id=r.attributes.weakness
                    or r.attributes.cwe_id
                    or "CWE-DESCONOCIDO",
                    cvss_score=r.attributes.severity_score
                    or mapear_cvss(r.attributes.severity_rating),
                    titulo=r.attributes.title,
                    fecha=r.attributes.created_at,
                    fuente_url=r.attributes.url,
                    tecnologias_detectadas=extraer_techs(r.attributes.title),
                )
            )
        return normalized

    def filter_3_relevancy(self, normalized_data: list[NormalizedReport]):
        print("[Pipeline][F3] Evaluando relevancia por empresa...")
        result: list[RelevancyReport] = []

        for rep in normalized_data:
            for empresa in self.company_repository.get_companies():
                techs = rep.tecnologias_detectadas
                stack = empresa.stack
                impactadas = [t for t in techs if t in stack] if techs else stack

                if impactadas or not techs:
                    result.append(
                        RelevancyReport(
                            fuente_id=rep.fuente_id,
                            cwe_id=rep.cwe_id,
                            cvss_score=rep.cvss_score,
                            titulo=rep.titulo,
                            fecha=rep.fecha,
                            fuente_url=rep.fuente_url,
                            tecnologias_detectadas=rep.tecnologias_detectadas,
                            empresa_id=empresa.id,
                            empresa_nombre=empresa.name,
                            impactadas=impactadas,
                        )
                    )

        print(f"[Pipeline][F3] {len(result)} pares empresa-vulnerabilidad relevantes")
        return result

    def filter_4_clasification(
        self, items: list[RelevancyReport]
    ) -> list[ClassifiedReport]:
        print("[Pipeline][F4] Calculando Índice de Riesgo Contextual (IRC)...")
        result: list[ClassifiedReport] = []
        companies_by_id = self.company_repository.get_companies_map()

        for item in items:
            company = companies_by_id.get(item.empresa_id)
            stack = company.stack if company else []
            impactadas = item.impactadas or []

            exposition = len(impactadas) / len(stack) if stack else 0.0
            irc_score = round(item.cvss_score * 0.6 + exposition * 10 * 0.4, 2)
            nivel = self.classification_service.calculate_irc_level(irc_score)

            result.append(
                ClassifiedReport(
                    fuente_id=item.fuente_id,
                    cwe_id=item.cwe_id,
                    cvss_score=item.cvss_score,
                    titulo=item.titulo,
                    fecha=item.fecha,
                    fuente_url=item.fuente_url,
                    tecnologias_detectadas=item.tecnologias_detectadas,
                    empresa_id=item.empresa_id,
                    empresa_nombre=item.empresa_nombre,
                    impactadas=item.impactadas,
                    irc_score=irc_score,
                    nivel_criticidad=nivel,
                )
            )
        return result

    def filter_5_enrichment(self, items: list[ClassifiedReport]) -> list[dict]:
        print("[Pipeline][F5] Enriqueciendo con mitigaciones NIST/OWASP...")
        return [
            {
                **item.model_dump(),
                "recomendacion": self.classification_service.get_mitigation(
                    item.cwe_id
                )["recomendacion"],
            }
            for item in items
        ]

    def filter_6_distribution(self, items: list[dict]):
        print("[Pipeline][F6] Distribuyendo alertas...")
        generadas = 0
        hace_24h = datetime.now(timezone.utc) - timedelta(hours=24)
        empresas = self.company_repository.get_companies_map()

        for item in items:
            empresa = empresas.get(item["empresa_id"])
            if not empresa:
                continue

            # Respetar umbral CVSS configurado por la empresa
            if item["cvss_score"] < empresa.threshold_cvss:
                continue

            # Deduplicar: no generar alerta si ya existe la misma empresa+CWE en 24h
            exists = self.alert_repository.get_if_alert_exists(
                company_id=empresa.id,
                cwe_id=item["cwe_id"],
                fecha_emision=hace_24h,
            )
            if exists:
                continue

            alert = Alert(
                company_id=empresa.id,
                cwe_id=item["cwe_id"],
                cwe_name=self.classification_service.get_mitigation(item["cwe_id"])[
                    "nombre"
                ],
                cvss_score=item["cvss_score"],
                irc_score=item["irc_score"],
                critical_level=item["nivel_criticidad"],
                affected_technologies=item["impactadas"],
                description=item["titulo"],
                recommendation=item["recomendacion"],
                source_url=item["fuente_url"],
                status="pending",
                emitted_at=self._now(),
                updated_at=None,
            )
            self.alert_repository.create_alert(alert)

            # Disparar notificación para críticas y altas
            if item["nivel_criticidad"] in ("Critico", "Alto"):
                self.notification_service.notify_alert(alert, empresa)

        return generadas
