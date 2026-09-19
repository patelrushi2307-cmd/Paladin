"""System status and configuration endpoints."""

from fastapi import APIRouter, Depends
from ..config import Settings
from ..dependencies import get_alert_repository, get_settings
from ..repositories import AlertRepository
from ..schemas.system import SystemStatus
from ..system_contract import ACTIVE_PROBING, INLINE_MITIGATION, ONE_WAY_ONLY, PAYLOAD_DECRYPTION
from ..ingest.runtime import runtime
from ..detectors.engine import detection_engine

router = APIRouter(prefix="/api/system", tags=["system"])


def current_status(repository: AlertRepository) -> SystemStatus:
    ingest_status = runtime.status()
    replay = runtime.controller.status()
    metrics = ingest_status.metrics
    return SystemStatus(
        service_status="healthy",
        ingest_status="running" if replay.state in {"RUNNING", "PAUSED", "STARTING"} else "ready",
        ingest_mode=replay.source_type or "passive",
        alerts_total=len(repository.list_alerts()),
        active_detectors=list(detection_engine.detectors),
        flows_per_second=metrics.flows_per_second,
        throughput_mbps=metrics.throughput_mbps,
        last_event_timestamp=metrics.last_event_timestamp,
        receive_only=ONE_WAY_ONLY,
        payload_decryption=PAYLOAD_DECRYPTION,
        return_path=not ONE_WAY_ONLY,
    )


@router.get("/status", response_model=SystemStatus)
def status(repository: AlertRepository = Depends(get_alert_repository)) -> SystemStatus:
    return current_status(repository)


@router.get("/config-summary")
def config_summary(settings: Settings = Depends(get_settings)) -> dict[str, object]:
    return {
        "app_env": settings.app_env,
        "backend_port": settings.backend_port,
        "frontend_port": settings.frontend_port,
        "detection_window_seconds": settings.detection_window_seconds,
        "security_posture": {
            "one_way_only": ONE_WAY_ONLY,
            "payload_decryption": PAYLOAD_DECRYPTION,
            "active_probing": ACTIVE_PROBING,
            "inline_mitigation": INLINE_MITIGATION,
        },
    }
