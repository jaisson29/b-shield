import enum
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AlertStatus(str, enum.Enum):
    pending = "pending"
    reviewing = "reviewing"
    mitigated = "mitigated"
    ignored = "ignored"


class CriticalLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    cwe_id: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    cwe_name: Mapped[str] = mapped_column(String(180), nullable=False)
    cvss_score: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False)
    irc_score: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    critical_level: Mapped[CriticalLevel] = mapped_column(
        Enum(CriticalLevel, name="critical_level_enum"),
        index=True,
        nullable=False,
    )
    affected_technologies: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, name="alert_status_enum"),
        index=True,
        nullable=False,
        default=AlertStatus.pending,
    )
    emitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
    )

    company = relationship("Company", back_populates="alerts")

    __table_args__ = (
        CheckConstraint("cvss_score >= 0 AND cvss_score <= 10", name="alerts_cvss_range_check"),
        CheckConstraint("irc_score >= 0", name="alerts_irc_non_negative_check"),
        Index("ix_alerts_company_status", "company_id", "status"),
        Index("ix_alerts_company_emitted_at", "company_id", "emitted_at"),
    )
