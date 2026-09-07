from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import IncidentStatus, SecurityIncident, UserRole
from app.schemas import IncidentRead
from app.security import require_roles

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentRead])
def list_incidents(db: Session = Depends(get_db), _: object = Depends(require_roles(UserRole.admin, UserRole.analyst))) -> list[SecurityIncident]:
    return db.query(SecurityIncident).order_by(SecurityIncident.created_at.desc()).limit(200).all()


@router.post("/{incident_id}/resolve", response_model=IncidentRead)
def resolve_incident(incident_id: int, db: Session = Depends(get_db), _: object = Depends(require_roles(UserRole.admin, UserRole.analyst))) -> SecurityIncident:
    incident = db.get(SecurityIncident, incident_id)
    if incident is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = IncidentStatus.resolved
    db.commit()
    db.refresh(incident)
    return incident