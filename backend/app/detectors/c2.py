"""Passive beacon-like recurrence detector."""

from typing import Any
from .base import ThreatDetector
from .base_utils import result, value, clamp
from ..schemas.detector import DetectorResult
from ..schemas.feature import FeatureVector


class C2ModelFeatures:
    names = ["iat_mean", "iat_std", "iat_cv", "periodicity_score", "repeated_destination_ratio", "destination_concentration", "flow_duration", "flows_total", "bytes_total", "packets_total"]


class C2BeaconDetector(ThreatDetector):
    name = "c2"
    version = "1.0.0"
    scopes = ("PAIR_WINDOW", "SOURCE_WINDOW")

    def __init__(self, minimum_observations: int = 5) -> None:
        self.minimum_observations = minimum_observations

    def initialize(self) -> None: pass

    def detect(self, feature_vector: FeatureVector, context: dict[str, Any]) -> list[DetectorResult]:
        if not self.supports_scope(feature_vector.scope): return []
        observations = value(feature_vector, "observation_count", value(feature_vector, "flows_total", 0))
        periodicity = value(feature_vector, "periodicity_score")
        cv = value(feature_vector, "iat_cv")
        repeated = value(feature_vector, "repeated_destination_ratio", context.get("repeated_destination_ratio", 0))
        if not isinstance(observations, (int, float)) or observations < self.minimum_observations:
            return [result(self.name, self.version, "C2_BEACON", feature_vector, 0, {"observation_count": observations}, [], C2ModelFeatures.names, applicability="insufficient_evidence")]
        regularity = periodicity if isinstance(periodicity, (int, float)) else (max(0, 1 - float(cv)) if isinstance(cv, (int, float)) else 0)
        concentration = value(feature_vector, "destination_concentration", 0) or 0
        raw_score = float(regularity) * .45 + float(repeated) * .35 + float(concentration) * .2
        score = clamp(raw_score if float(repeated) >= 0.6 and float(concentration) >= 0.5 else raw_score * float(repeated))
        reasons = []
        if regularity >= .7: reasons.append("strong_periodicity")
        if repeated >= .7: reasons.append("repeated_destination")
        if regularity >= .7 and (value(feature_vector, "bytes_per_sec", 0) or 0) < 100_000: reasons.append("persistent_low_volume_connection")
        evidence = {name: value(feature_vector, name) for name in C2ModelFeatures.names if value(feature_vector, name) is not None}
        evidence["observation_count"] = observations
        return [result(self.name, self.version, "C2_BEACON", feature_vector, score, evidence, reasons, C2ModelFeatures.names)]

    def health(self) -> dict[str, str]: return {"status": "running", "name": self.name}
