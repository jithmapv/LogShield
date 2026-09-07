from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import EventType, IncidentSeverity, IncidentStatus, LogTelemetry, SecurityIncident
from app.webhooks import dispatch_incident, remediation_payload


def detect_brute_force(db: Session, now: datetime | None = None) -> list[SecurityIncident]:
    end = now or datetime.now(timezone.utc)
    start = end - timedelta(seconds=60)
    rows = (
        db.query(LogTelemetry.source_ip, func.count(LogTelemetry.id).label("attempts"))
        .filter(LogTelemetry.event_type == EventType.auth_failure, LogTelemetry.timestamp >= start, LogTelemetry.timestamp <= end)
        .group_by(LogTelemetry.source_ip)
        .having(func.count(LogTelemetry.id) >= get_settings().brute_force_threshold)
        .all()
    )
    incidents = []
    for source_ip, attempts in rows:
        exists = db.query(SecurityIncident).filter(SecurityIncident.rule_triggered == "brute_force", SecurityIncident.source_ip == source_ip, SecurityIncident.created_at >= start).first()
        if exists:
            continue
        incident = SecurityIncident(rule_triggered="brute_force", severity=IncidentSeverity.high, status=IncidentStatus.open, source_ip=source_ip, incident_metadata={"attempts": attempts, "remediation": remediation_payload(source_ip)})
        db.add(incident)
        incidents.append(incident)
    db.commit()
    return incidents


def detect_api_spikes(db: Session, now: datetime | None = None) -> list[SecurityIncident]:
    end = now or datetime.now(timezone.utc)
    start = end - timedelta(minutes=1)
    rows = db.query(LogTelemetry.source_ip, func.count(LogTelemetry.id).label("events")).filter(LogTelemetry.timestamp >= start, LogTelemetry.timestamp <= end).group_by(LogTelemetry.source_ip).having(func.count(LogTelemetry.id) >= get_settings().api_spike_threshold).all()
    incidents = []
    for source_ip, events in rows:
        exists = db.query(SecurityIncident).filter(SecurityIncident.rule_triggered == "api_spike", SecurityIncident.source_ip == source_ip, SecurityIncident.created_at >= start).first()
        if exists:
            continue
        incident = SecurityIncident(rule_triggered="api_spike", severity=IncidentSeverity.critical, status=IncidentStatus.open, source_ip=source_ip, incident_metadata={"events": events, "remediation": remediation_payload(source_ip)})
        db.add(incident)
        incidents.append(incident)
    db.commit()
    return incidents


async def publish_incidents(incidents: list[SecurityIncident]) -> None:
    for incident in incidents:
        await dispatch_incident({"incident_id": incident.id, "rule_triggered": incident.rule_triggered, "severity": incident.severity.value, "source_ip": incident.source_ip})