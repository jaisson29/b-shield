import os
from collections.abc import Generator
from datetime import datetime, timezone

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/bshield",
)


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Importa modelos para registrar sus tablas en el metadata de SQLAlchemy.
    from app.models import alert, company, ingestion_log

    Base.metadata.create_all(bind=engine)
    _ensure_integer_pk_defaults()


def _ensure_integer_pk_defaults() -> None:
    # Repara esquemas legacy donde la PK integer no tiene secuencia/default.
    tables = ("companies", "alerts")

    with engine.begin() as conn:
        for table in tables:
            seq = f"public.{table}_id_seq"
            conn.execute(text(f"CREATE SEQUENCE IF NOT EXISTS {seq}"))
            conn.execute(text(f"ALTER SEQUENCE {seq} OWNED BY public.{table}.id"))
            conn.execute(
                text(
                    f"ALTER TABLE public.{table} "
                    f"ALTER COLUMN id SET DEFAULT nextval('{seq}')"
                )
            )
            conn.execute(
                text(
                    f"SELECT setval('{seq}', "
                    f"COALESCE((SELECT MAX(id) FROM public.{table}), 0) + 1, false)"
                )
            )


def seed_db() -> None:
    from app.models.alert import Alert, AlertStatus, CriticalLevel
    from app.models.company import Company
    from app.models.ingestion_log import IngestionLog
    from app.store import store

    status_map = {
        "pendiente": AlertStatus.pending,
        "revisada": AlertStatus.reviewing,
        "mitigada": AlertStatus.mitigated,
        "ignorada": AlertStatus.ignored,
    }
    level_map = {
        "bajo": CriticalLevel.low,
        "medio": CriticalLevel.medium,
        "alto": CriticalLevel.high,
        "critico": CriticalLevel.critical,
    }

    def parse_iso(value: str | None) -> datetime | None:
        if not value:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    def parse_legacy_int_id(value: str | None, fallback: int) -> int:
        if not value:
            return fallback
        tail = value.split("-")[-1]
        if tail.isdigit():
            return int(tail)
        return fallback

    # Mapea IDs legacy (emp-001) a IDs enteros estables.
    legacy_company_ids = sorted(store.companies.keys())
    company_id_map = {legacy_id: idx for idx, legacy_id in enumerate(legacy_company_ids, 1)}

    with SessionLocal() as db:
        for legacy_id in legacy_company_ids:
            company_data = store.companies[legacy_id]
            int_id = company_id_map[legacy_id]
            existing_company = db.get(Company, int_id)

            if existing_company is None:
                db.add(
                    Company(
                        id=int_id,
                        name=company_data["nombre"],
                        occupation=company_data["sector"],
                        size=company_data["tamano"],
                        country=company_data["pais"],
                        stack=company_data["stack"],
                        threshold_cvss=company_data["umbral_cvss"],
                        email=company_data["contacto_email"],
                        created_at=parse_iso(company_data["creado_en"]) or datetime.now(timezone.utc),
                        updated_at=parse_iso(company_data["actualizado_en"]),
                    )
                )

        db.flush()

        existing_alert_keys = {
            (row.company_id, row.cwe_id, row.cwe_name)
            for row in db.query(Alert.company_id, Alert.cwe_id, Alert.cwe_name).all()
        }
        existing_alert_ids = {row.id for row in db.query(Alert.id).all()}

        for idx, alert_data in enumerate(store.alerts, 1):
            company_id = company_id_map.get(alert_data["empresa_id"])
            if company_id is None:
                continue

            alert_id = parse_legacy_int_id(alert_data.get("id"), idx)
            alert_key = (company_id, alert_data["cwe_id"], alert_data["cwe_nombre"])
            if alert_id in existing_alert_ids or alert_key in existing_alert_keys:
                continue

            db.add(
                Alert(
                    id=alert_id,
                    company_id=company_id,
                    cwe_id=alert_data["cwe_id"],
                    cwe_name=alert_data["cwe_nombre"],
                    cvss_score=alert_data["cvss_score"],
                    irc_score=alert_data["irc_score"],
                    critical_level=level_map[alert_data["nivel_criticidad"].strip().lower()],
                    affected_technologies=alert_data["tecnologias_afectadas"],
                    description=alert_data["descripcion"],
                    recommendation=alert_data["recomendacion"],
                    source_url=alert_data["fuente_url"],
                    status=status_map[alert_data["estado"].strip().lower()],
                    emitted_at=parse_iso(alert_data["fecha_emision"]) or datetime.now(timezone.utc),
                    updated_at=parse_iso(alert_data["fecha_actualizacion"]),
                )
            )
            existing_alert_ids.add(alert_id)
            existing_alert_keys.add(alert_key)

        for log_data in store.ingestion_logs:
            existing_log = (
                db.query(IngestionLog)
                .filter(
                    IngestionLog.status == log_data["estado"],
                    IngestionLog.started_at == parse_iso(log_data["inicio"]),
                    IngestionLog.ended_at == parse_iso(log_data["fin"]),
                    IngestionLog.received_reports == log_data["reportes_recibidos"],
                    IngestionLog.generated_alerts == log_data["alertas_generadas"],
                    IngestionLog.error == log_data["error"],
                )
                .first()
            )
            if existing_log is None:
                db.add(
                    IngestionLog(
                        status=log_data["estado"],
                        started_at=parse_iso(log_data["inicio"]),
                        ended_at=parse_iso(log_data["fin"]),
                        received_reports=log_data["reportes_recibidos"],
                        generated_alerts=log_data["alertas_generadas"],
                        error=log_data["error"],
                    )
                )

        db.commit()
