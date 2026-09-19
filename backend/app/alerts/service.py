"""Fusion, deduplication, correlation, and alert publication service."""

from collections import deque
from datetime import timedelta
from hashlib import sha256
from uuid import uuid4
from ..repositories import AlertRepository
from ..schemas.alert import Alert, Severity, ThreatClass
from ..schemas.detector import DetectorResult
from ..scoring.fusion import ThreatScoreFusion


class AlertService:
    def __init__(self, repository: AlertRepository, fusion: ThreatScoreFusion | None = None, dedup_seconds: int = 30) -> None:
        self.repository = repository
        self.fusion = fusion or ThreatScoreFusion()
        self.dedup_seconds = dedup_seconds
        self.events: deque[tuple[str, Alert]] = deque(maxlen=500)

    def process(self, results: list[DetectorResult], context: dict | None = None) -> Alert | None:
        applicable = [result for result in results if result.detected and result.applicability == "applicable"]
        assessment = self.fusion.assess(applicable)
        if not assessment or not applicable:
            return None
        primary = max(applicable, key=lambda item: item.score)
        timestamp = primary.timestamp
        if timestamp is None:
            return None
        source = primary.source_ip or "unknown"
        destination = primary.destination_ip or "unknown"
        protocol = primary.protocol or "unknown"
        subtype = assessment.subtype
        dedup_key = "|".join((source, destination, assessment.threat_class, subtype or "", protocol))
        duplicate = self.repository.find_recent_duplicate(dedup_key, timestamp - timedelta(seconds=self.dedup_seconds))
        if duplicate:
            updated = duplicate.model_copy(update={"last_seen": timestamp, "occurrence_count": duplicate.occurrence_count + 1, "evidence": assessment.evidence, "confidence_score": assessment.confidence, "severity": Severity(assessment.severity)})
            self.repository.update(updated, dedup_key); self.events.append(("ALERT_UPDATED", updated)); return updated
        alert = Alert(alert_id=str(uuid4()), timestamp=timestamp, flow_id=primary.flow_id if hasattr(primary, "flow_id") else primary.detector + "-" + timestamp.isoformat(), threat_class=ThreatClass(assessment.threat_class), severity=Severity(assessment.severity), confidence_score=assessment.confidence, source_ip=source, destination_ip=destination, protocol=protocol, evidence=assessment.evidence, detector=primary.detector, detector_version=primary.detector_version, model_version=primary.model_version, observation_window_ms=5000, subtype=subtype, scope=primary.scope, replay_session_id=primary.replay_session_id, feature_schema_version="1.0", created_at=timestamp, first_seen=timestamp, last_seen=timestamp, evidence_completeness=assessment.evidence_completeness, correlation_id=self._correlation_id(source, timestamp), why_flagged=assessment.why_flagged)
        self.repository.create(alert, dedup_key); self.events.append(("ALERT_CREATED", alert)); return alert

    def _correlation_id(self, source: str, timestamp) -> str | None:
        recent = self.repository.list(limit=50, source_ip=source)
        for item in recent:
            if item.timestamp and abs((timestamp - item.timestamp).total_seconds()) <= 300:
                return item.correlation_id or sha256(f"{source}:{item.timestamp.isoformat()}".encode()).hexdigest()[:16]
        return None

    def latest_event(self) -> tuple[str, Alert] | None:
        return self.events[-1] if self.events else None


alert_service: AlertService | None = None
