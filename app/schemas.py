from datetime import datetime, timezone
from ipaddress import ip_address
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.entities import EventType, IncidentSeverity, IncidentStatus, UserRole


class LogCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    timestamp: datetime | None = None
    source_ip: str = Field(pattern=r"^(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)$|^[0-9a-fA-F:]+$")
    event_type: EventType
    user_id: int | None = Field(default=None, ge=1)
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("source_ip")
    @classmethod
    def validate_ip(cls, value: str) -> str:
        try:
            ip_address(value)
        except ValueError as exc:
            raise ValueError("source_ip must be a valid IPv4 or IPv6 address") from exc
        return value

    @field_validator("timestamp", mode="before")
    @classmethod
    def normalize_timestamp(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


class LogRead(LogCreate):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=3, max_length=128, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=12, max_length=128)
    role: UserRole = UserRole.client


class IncidentRead(BaseModel):
    id: int
    rule_triggered: str
    severity: IncidentSeverity
    status: IncidentStatus
    source_ip: str
    created_at: datetime
    metadata: dict[str, Any] = Field(validation_alias="incident_metadata", serialization_alias="metadata")

    model_config = ConfigDict(from_attributes=True)