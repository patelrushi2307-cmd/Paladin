from datetime import datetime, timedelta, timezone
from pathlib import Path
from app.alerts.service import AlertService
from app.repositories import AlertRepository
from app.schemas.detector import DetectorResult


def detector(score: float, timestamp: datetime, detector_name: str = "c2") -> DetectorResult:
    return DetectorResult(detector=detector_name, detector_version="1.0.0", threat_class="C2_BEACON", detected=True, score=score, rule_score=score, evidence={"periodicity_score": .95, "iat_cv": .01}, reasons=["strong_periodicity"], scope="SOURCE_WINDOW", evidence_completeness=.8, timestamp=timestamp, source_ip="10.0.0.8", destination_ip="8.8.8.8", protocol="TCP", flow_id="flow-1")


def test_alert_fusion_and_dedup(tmp_path: Path):
    repository = AlertRepository(f"sqlite:///{tmp_path / 'alerts.db'}")
    service = AlertService(repository, dedup_seconds=30)
    timestamp = datetime.now(timezone.utc)
    first = service.process([detector(.9, timestamp)])
    second = service.process([detector(.8, timestamp + timedelta(seconds=1))])
    assert first is not None
    assert second is not None
    assert second.alert_id == first.alert_id
    assert second.occurrence_count == 2
    assert repository.count() == 1


def test_alert_lifecycle_and_summary(tmp_path: Path):
    repository = AlertRepository(f"sqlite:///{tmp_path / 'alerts.db'}")
    service = AlertService(repository)
    alert = service.process([detector(.6, datetime.now(timezone.utc), "recon")])
    assert alert is not None
    updated = repository.set_status(alert.alert_id, "ACKNOWLEDGED")
    assert updated and updated.status == "ACKNOWLEDGED"
    assert repository.summary()["total"] == 1
