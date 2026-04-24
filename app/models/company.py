import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(160), unique=True, nullable=False, index=True)
    occupation: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    size: Mapped[str] = mapped_column(String(40), nullable=False)
    country: Mapped[str] = mapped_column(String(80), nullable=False, default="Colombia")
    stack: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    threshold_cvss: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False, default=7.0)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
    )

    alerts = relationship("Alert", back_populates="company", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("threshold_cvss >= 0 AND threshold_cvss <= 10", name="companies_threshold_cvss_range_check"),
    )
