"""Detector observability API."""

from fastapi import APIRouter, Query
from ..detectors.engine import detection_engine
from ..schemas.detector import DetectionStatus, DetectorResult

router = APIRouter(prefix="/api/detectors", tags=["detectors"])


@router.get("/status", response_model=DetectionStatus)
def detector_status() -> DetectionStatus:
    return detection_engine.status()


@router.get("/results/recent", response_model=list[DetectorResult])
def recent_results(detector: str | None = Query(default=None)) -> list[DetectorResult]:
    return detection_engine.recent(detector)


@router.get("/{detector_name}/status")
def detector_by_name(detector_name: str):
    return next((item for item in detection_engine.status().detectors if item.name == detector_name), {"name": detector_name, "enabled": False, "status": "NOT_ENABLED"})
