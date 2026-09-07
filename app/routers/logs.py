from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import LogTelemetry
from app.schemas import LogCreate, LogRead
from app.security import require_api_key

router = APIRouter(prefix="/api/v1/logs", tags=["logs"])


@router.post("", response_model=LogRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_api_key)])
def ingest_log(log: LogCreate, db: Session = Depends(get_db)) -> LogTelemetry:
    telemetry = LogTelemetry(**log.model_dump(exclude_none=True))
    if telemetry.timestamp is None:
        telemetry.timestamp = datetime.now(timezone.utc)
    db.add(telemetry)
    db.commit()
    db.refresh(telemetry)
    return telemetry