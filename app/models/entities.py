import enum
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database import Base

json_payload = JSON().with_variant(JSONB, "postgresql")


class UserRole(str, enum.Enum):
    admin = "admin"
    analyst = "analyst"
    client = "client"


class EventType(str, enum.Enum):
    auth_failure = "auth_failure"
    auth_success = "auth_success"
    api_spike = "api_spike"
    data_access = "data_access"


class IncidentSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IncidentStatus(str, enum.Enum):
    open = "open"
    resolved = "resolved"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.client, index=True)

    telemetry: Mapped[list["LogTelemetry"]] = relationship(back_populates="user")


class LogTelemetry(Base):
    __tablename__ = "log_telemetry"
    __table_args__ = (
        Index("ix_log_telemetry_timestamp_source_ip", "timestamp", "source_ip"),
        Index("ix_log_telemetry_event_timestamp", "event_type", "timestamp"),
        Index("ix_log_telemetry_auth_failures", "source_ip", "timestamp", postgresql_where="event_type = 'auth_failure'"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    source_ip: Mapped[str] = mapped_column(String(45), index=True)
    event_type: Mapped[EventType] = mapped_column(Enum(EventType), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(json_payload)

    user: Mapped[User | None] = relationship(back_populates="telemetry")


class SecurityIncident(Base):
    __tablename__ = "security_incidents"
    __table_args__ = (
        Index("ix_incidents_status_created_at", "status", "created_at"),
        Index("ix_incidents_rule_source", "rule_triggered", "source_ip"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_triggered: Mapped[str] = mapped_column(String(128), index=True)
    severity: Mapped[IncidentSeverity] = mapped_column(Enum(IncidentSeverity), index=True)
    status: Mapped[IncidentStatus] = mapped_column(Enum(IncidentStatus), default=IncidentStatus.open, index=True)
    source_ip: Mapped[str] = mapped_column(String(45), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    incident_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", json_payload, default=dict)