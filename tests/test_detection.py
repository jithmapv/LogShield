from datetime import datetime, timedelta, timezone

from app.engine.detector import detect_brute_force
from app.models import EventType, LogTelemetry, SecurityIncident


def test_brute_force_creates_one_incident(client):
    db = client.app.state.test_session_factory()
    now = datetime.now(timezone.utc)
    for _ in range(5):
        db.add(LogTelemetry(timestamp=now - timedelta(seconds=5), source_ip="10.0.0.9", event_type=EventType.auth_failure, payload={}))
    db.commit()
    incidents = detect_brute_force(db, now)
    assert len(incidents) == 1
    assert db.query(SecurityIncident).count() == 1
    assert detect_brute_force(db, now) == []
    db.close()