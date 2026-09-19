"""Passive outbound asymmetry detector."""

from typing import Any
from .base import ThreatDetector
from .base_utils import result, value, clamp
from ..schemas.detector import DetectorResult
from ..schemas.feature import FeatureVector


class ExfilModelFeatures:
    names = ["outbound_bytes", "inbound_bytes", "outbound_rate", "outbound_inbound_ratio", "flow_duration", "bytes_total", "destination_concentration", "unique_dst_hosts", "current_bytes_vs_baseline"]


class ExfiltrationDetector(ThreatDetector):
    name = "exfiltration"
    version = "1.0.0"
    scopes = ("FLOW", "SOURCE_WINDOW")

    def initialize(self) -> None: pass

    def detect(self, feature_vector: FeatureVector, context: dict[str, Any]) -> list[DetectorResult]:
        if not self.supports_scope(feature_vector.scope): return []
        direction = value(feature_vector, "direction_class", context.get("direction"))
        if direction not in {"OUTBOUND", "outbound"}:
            return [result(self.name, self.version, "DATA_EXFILTRATION", feature_vector, 0, {"direction_class": direction}, [], ExfilModelFeatures.names, applicability="insufficient_direction_evidence")]
        outbound = value(feature_vector, "outbound_bytes")
        inbound = value(feature_vector, "inbound_bytes")
        ratio = value(feature_vector, "outbound_inbound_ratio")
        rate = value(feature_vector, "outbound_rate")
        duration = value(feature_vector, "flow_duration")
        volume = min(1, float(outbound) / 10_000_000) if isinstance(outbound, (int, float)) else 0
        asymmetry = min(1, float(ratio) / 10) if isinstance(ratio, (int, float)) else 0
        sustained = min(1, float(rate) / 1_000_000) * min(1, float(duration) / 60) if isinstance(rate, (int, float)) and isinstance(duration, (int, float)) else 0
        score = clamp(volume * .35 + asymmetry * .35 + sustained * .2 + (0.1 if value(feature_vector, "current_bytes_vs_baseline", 0) > 0 else 0))
        reasons = []
        if volume >= .5: reasons.append("unusually_high_outbound_volume")
        if asymmetry >= .5: reasons.append("strong_outbound_inbound_asymmetry")
        if sustained >= .5: reasons.append("sustained_outbound_transfer")
        evidence = {name: value(feature_vector, name) for name in ExfilModelFeatures.names if value(feature_vector, name) is not None}
        return [result(self.name, self.version, "DATA_EXFILTRATION", feature_vector, score, evidence, reasons, ExfilModelFeatures.names)]

    def health(self) -> dict[str, str]: return {"status": "running", "name": self.name}
