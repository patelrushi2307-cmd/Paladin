"""Passive volumetric and protocol flood indicators."""

from typing import Any
from .base import ThreatDetector
from .base_utils import not_applicable, result, value, clamp
from ..schemas.detector import DetectorResult
from ..schemas.feature import FeatureVector


class DDoSModelFeatures:
    names = ["packets_per_sec", "bytes_per_sec", "flows_per_sec", "unique_src_count", "source_ip_entropy", "destination_concentration", "syn_ratio", "ack_ratio", "udp_ratio", "burst_packets_per_sec", "burst_bytes_per_sec"]


class DDoSDetector(ThreatDetector):
    name = "ddos"
    version = "1.0.0"
    scopes = ("GLOBAL_WINDOW", "DESTINATION_WINDOW", "SOURCE_WINDOW", "FLOW")

    def __init__(self, packet_rate_threshold: float = 1000, byte_rate_threshold: float = 1_000_000, source_entropy_threshold: float = 3, concentration_threshold: float = 0.75) -> None:
        self.packet_rate_threshold = packet_rate_threshold
        self.byte_rate_threshold = byte_rate_threshold
        self.source_entropy_threshold = source_entropy_threshold
        self.concentration_threshold = concentration_threshold

    def initialize(self) -> None: pass

    def detect(self, feature_vector: FeatureVector, context: dict[str, Any]) -> list[DetectorResult]:
        if not self.supports_scope(feature_vector.scope):
            return []
        names = DDoSModelFeatures.names
        packets = value(feature_vector, "packets_per_sec")
        bytes_rate = value(feature_vector, "bytes_per_sec")
        source_entropy = value(feature_vector, "source_ip_entropy")
        concentration = value(feature_vector, "destination_concentration")
        syn = value(feature_vector, "syn_ratio")
        udp = value(feature_vector, "udp_ratio")
        components = [min(1, packets / self.packet_rate_threshold) if isinstance(packets, (int, float)) else 0, min(1, bytes_rate / self.byte_rate_threshold) if isinstance(bytes_rate, (int, float)) else 0, min(1, source_entropy / (self.source_entropy_threshold * 2)) if isinstance(source_entropy, (int, float)) else 0, concentration if isinstance(concentration, (int, float)) else 0, syn if isinstance(syn, (int, float)) else 0, udp if isinstance(udp, (int, float)) else 0]
        score = clamp(sum(components) / len(components))
        evidence = {name: value(feature_vector, name) for name in names if value(feature_vector, name) is not None}
        reasons = []
        if components[0] >= 0.5: reasons.append("elevated_packet_rate")
        if components[2] >= 0.5: reasons.append("high_source_diversity")
        if components[3] >= self.concentration_threshold: reasons.append("high_destination_concentration")
        if components[4] >= 0.7: reasons.append("syn_dominant_behavior")
        if components[5] >= 0.7: reasons.append("udp_flood_like_behavior")
        return [result(self.name, self.version, "DDOS", feature_vector, score, evidence, reasons, names)]

    def health(self) -> dict[str, str]: return {"status": "running", "name": self.name}
