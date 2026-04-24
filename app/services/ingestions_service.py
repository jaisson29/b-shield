import asyncio

import httpx
from app.infrastructure.h1_client import (
    fetch_recent_hacktivity,
    mapear_cvss,
)
from app.services.classifcation_service import calculate_irc_level
from app.services.types.ingestion_types import (
    ClassifiedReport,
    NormalizedReport,
    RawReport,
    RelevancyReport,
)
from app.store import Store


class IngestionsService:
    def __init__(self, db: Store):
        self.db = db

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
        # Aquí iría la lógica real de ingesta desde HackerOne API.
        # Por ahora, es un mock que simula la respuesta de la API.
        raw_data = await self.filter_1_ingestion()
        normalized_data = await self.filter_2_normalization(raw_data)

        return normalized_data

    def _now():
        from datetime import datetime, timezone

        return datetime.now(timezone.utc)

    async def filter_1_ingestion(self) -> list[RawReport]:
        async with httpx.AsyncClient() as client:
            client.base_url = "https://api.hackerone.com/v1"

            response = await fetch_recent_hacktivity()
            return [RawReport(**r) for r in response]

    async def filter_2_normalization(
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
            for empresa in self.db.companies.values():
                techs = rep.tecnologias_detectadas
                stack = empresa["stack"]
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
                            empresa_id=empresa["id"],
                            empresa_nombre=empresa["nombre"],
                            impactadas=impactadas,
                        )
                    )

        print(f"[Pipeline][F3] {len(result)} pares empresa-vulnerabilidad relevantes")
        return result

    def filter_4_clasification(self, items: list[RelevancyReport]) -> list[ClassifiedReport]:
        print("[Pipeline][F4] Calculando Índice de Riesgo Contextual (IRC)...")
        result: list[ClassifiedReport] = []

        for item in items:
            company = self.db.companies.get(item.empresa_id)
            stack = company["stack"] if company else []
            impactadas = item.impactadas or []

            exposition = len(impactadas) / len(stack) if stack else 0.0
            irc_score = round(item.cvss_score * 0.6 + exposition * 10 * 0.4, 2)
            nivel = calculate_irc_level(irc_score)

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
