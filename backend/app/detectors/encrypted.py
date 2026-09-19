"""Metadata-only encrypted-session anomaly detector."""

from typing import Any
from .base import ThreatDetector
from .base_utils import not_applicable, result, value, clamp
from ..schemas.detector import DetectorResult
from ..schemas.feature import FeatureVector
from ..system_contract import PAYLOAD_DECRYPTION


class EncryptedModelFeatures:
    names = ["tls_sni_present", "tls_version", "tls_ja3", "tls_ja3s", "tls_ja4", "packet_size_mean", "packet_size_std", "iat_mean", "iat_std", "iat_cv", "periodicity_score", "flow_duration", "bytes_total", "packets_total"]


class EncryptedTrafficDetector(ThreatDetector):
    name = "encrypted_malware"
    version = "1.0.0"
    scopes = ("FLOW", "SOURCE_WINDOW", "PAIR_WINDOW")

    def initialize(self) -> None:
        if PAYLOAD_DECRYPTION:
            raise RuntimeError("EncryptedTrafficDetector cannot run with payload decryption enabled")

    def detect(self, feature_vector: FeatureVector, context: dict[str, Any]) -> list[DetectorResult]:
        if not self.supports_scope(feature_vector.scope): return []
        available = value(feature_vector, "tls_metadata_available", False)
        protocol = str(value(feature_vector, "protocol", "")).upper()
        if not available and protocol not in {"TLS", "QUIC"}: return [not_applicable(self.name, self.version, "ENCRYPTED_MALWARE", feature_vector, EncryptedModelFeatures.names)]
        packet_std = value(feature_vector, "packet_size_std")
        timing_cv = value(feature_vector, "iat_cv")
        periodicity = value(feature_vector, "periodicity_score")
        size_signal = min(1, float(packet_std) / 300) if isinstance(packet_std, (int, float)) else 0
        timing_signal = min(1, float(timing_cv)) if isinstance(timing_cv, (int, float)) else 0
        periodic_signal = float(periodicity) if isinstance(periodicity, (int, float)) else 0
        has_fp = 0.2 if value(feature_vector, "tls_fingerprint") is not None else 0.0
        score = clamp(size_signal * .35 + timing_signal * .25 + periodic_signal * .2 + has_fp)
        reasons = []
        if size_signal >= .5: reasons.append("unusual_packet_size_distribution")
        if timing_signal >= .5 or periodic_signal >= .7: reasons.append("timing_pattern_anomaly")
        if value(feature_vector, "tls_fingerprint") is not None: reasons.append("unusual_fingerprint_context")
        evidence = {name: value(feature_vector, name) for name in EncryptedModelFeatures.names if value(feature_vector, name) is not None}
        evidence["payload_decryption"] = False
        return [result(self.name, self.version, "ENCRYPTED_MALWARE", feature_vector, score, evidence, reasons, EncryptedModelFeatures.names)]

    def health(self) -> dict[str, str]: return {"status": "running", "name": self.name}
