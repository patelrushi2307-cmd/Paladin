"""Alert history and lifecycle API."""
from fastapi import APIRouter, Depends, HTTPException, Query
from ..dependencies import get_alert_repository
from ..repositories import AlertRepository
from ..schemas.alert import Alert
router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("", response_model=list[Alert])
def alerts(repository: AlertRepository = Depends(get_alert_repository), limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0), threat_class: str | None = None, severity: str | None = None, status: str | None = None, source_ip: str | None = None, destination_ip: str | None = None) -> list[Alert]:
    return repository.list(limit=limit, offset=offset, threat_class=threat_class, severity=severity, status=status, source_ip=source_ip, destination_ip=destination_ip)

@router.get("/summary")
def summary(repository: AlertRepository = Depends(get_alert_repository)):
    return repository.summary()

@router.get("/{alert_id}", response_model=Alert)
def alert(alert_id: str, repository: AlertRepository = Depends(get_alert_repository)) -> Alert:
    item = repository.get(alert_id)
    if not item: raise HTTPException(status_code=404, detail="Alert not found")
    return item

@router.get("/{alert_id}/related", response_model=list[Alert])
def related(alert_id: str, repository: AlertRepository = Depends(get_alert_repository)) -> list[Alert]:
    item = repository.get(alert_id)
    if not item or not item.correlation_id: return []
    return [candidate for candidate in repository.list(limit=500) if candidate.correlation_id == item.correlation_id and candidate.alert_id != alert_id]

@router.post("/{alert_id}/acknowledge", response_model=Alert)
def acknowledge(alert_id: str, repository: AlertRepository = Depends(get_alert_repository)) -> Alert:
    item = repository.set_status(alert_id, "ACKNOWLEDGED")
    if not item: raise HTTPException(status_code=404, detail="Alert not found")
    return item

@router.post("/{alert_id}/resolve", response_model=Alert)
def resolve(alert_id: str, repository: AlertRepository = Depends(get_alert_repository)) -> Alert:
    item = repository.set_status(alert_id, "RESOLVED")
    if not item: raise HTTPException(status_code=404, detail="Alert not found")
    return item
