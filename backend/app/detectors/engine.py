"""Shared bounded detector pipeline."""

from collections import deque
import time
from ..schemas.detector import DetectorResult, DetectionStatus, DetectorStatus
from ..schemas.feature import FeatureVector
from .ddos import DDoSDetector
from .recon import ReconDetector
from .c2 import C2BeaconDetector
from .exfil import ExfiltrationDetector
from .dga import DgaDnsDetector
from .encrypted import EncryptedTrafficDetector


class DetectionEngine:
    def __init__(self) -> None:
        self.detectors = {detector.name: detector for detector in (DDoSDetector(), ReconDetector(), C2BeaconDetector(), ExfiltrationDetector(), DgaDnsDetector(), EncryptedTrafficDetector())}
        for detector in self.detectors.values(): detector.initialize()
        self.results: deque[DetectorResult] = deque(maxlen=1000)
        self.queue_maxsize = 10000
        self.dropped = 0
        self.errors = 0
        self.latencies: dict[str, deque[float]] = {name: deque(maxlen=500) for name in self.detectors}
        self.emitted = 0

    def register(self, detector) -> None:
        detector.initialize()
        self.detectors[detector.name] = detector
        self.latencies.setdefault(detector.name, deque(maxlen=500))

    def process(self, vector: FeatureVector, context: dict | None = None) -> list[DetectorResult]:
        output = []
        for name, detector in self.detectors.items():
            if not detector.supports_scope(vector.scope): continue
            started = time.perf_counter()
            try:
                results = detector.detect(vector, context or {})
                self.latencies[name].append((time.perf_counter() - started) * 1000)
                for item in results:
                    item = item.model_copy(update={"source_ip": (context or {}).get("source_ip"), "destination_ip": (context or {}).get("destination_ip"), "protocol": (context or {}).get("protocol"), "replay_session_id": (context or {}).get("replay_session_id"), "flow_id": vector.flow_id})
                    if len(self.results) >= self.results.maxlen: self.dropped += 1
                    self.results.append(item); self.emitted += 1; output.append(item)
            except Exception:
                self.errors += 1
        return output

    def recent(self, detector_name: str | None = None) -> list[DetectorResult]:
        values = list(reversed(self.results))
        return [item for item in values if detector_name is None or item.detector == detector_name]

    def status(self) -> DetectionStatus:
        latencies = [latency for values in self.latencies.values() for latency in values]
        average = sum(latencies) / len(latencies) if latencies else 0
        statuses = []
        for name, detector in self.detectors.items():
            values = self.latencies.get(name, [])
            statuses.append(DetectorStatus(name=name, enabled=True, status=detector.health().get("status", "running").upper(), version=detector.version, scopes=list(detector.scopes), results_emitted=sum(1 for item in self.results if item.detector == name), errors=0, average_latency_ms=sum(values) / len(values) if values else 0))
        return DetectionStatus(active_detectors=list(self.detectors), detector_count=len(self.detectors), detector_results_emitted=self.emitted, detector_results_dropped=self.dropped, average_latency_ms=average, errors=self.errors, detectors=statuses)


detection_engine = DetectionEngine()
