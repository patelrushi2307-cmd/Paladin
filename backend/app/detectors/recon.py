"""Passive reconnaissance and scan behavior indicators."""

from typing import Any
from .base import ThreatDetector
from .base_utils import result, value, clamp
from ..schemas.detector import DetectorResult
from ..schemas.feature import FeatureVector


class ReconModelFeatures:
    names = ["fanout_hosts", "fanout_ports", "scan_velocity", "unique_dst_hosts", "unique_dst_ports", "syn_ratio", "destination_ip_entropy", "packets_per_sec"]


class ReconDetector(ThreatDetector):
    name = "recon"
    version = "1.0.0"
    scopes = ("SOURCE_WINDOW", "PAIR_WINDOW", "FLOW")

    def __init__(self, host_threshold: float = 8, port_threshold: float = 8, velocity_threshold: float = 3) -> None:
        self.host_threshold, self.port_threshold, self.velocity_threshold = host_threshold, port_threshold, velocity_threshold

    def initialize(self) -> None: pass

    def detect(self, feature_vector: FeatureVector, context: dict[str, Any]) -> list[DetectorResult]:
        if not self.supports_scope(feature_vector.scope): return []
        hosts, ports, velocity = value(feature_vector, "fanout_hosts"), value(feature_vector, "fanout_ports"), value(feature_vector, "scan_velocity")
        host_score = min(1, hosts / self.host_threshold) if isinstance(hosts, (int, float)) else 0
        port_score = min(1, ports / self.port_threshold) if isinstance(ports, (int, float)) else 0
        velocity_score = min(1, velocity / self.velocity_threshold) if isinstance(velocity, (int, float)) else 0
        syn = value(feature_vector, "syn_ratio") or 0
        score = clamp(host_score * 0.4 + port_score * 0.3 + velocity_score * 0.25 + float(syn) * 0.05)
        reasons = []
        if host_score >= .5: reasons.append("high_host_fanout")
        if port_score >= .5: reasons.append("high_port_fanout")
        if velocity_score >= .5: reasons.append("rapid_destination_exploration")
        evidence = {name: value(feature_vector, name) for name in ReconModelFeatures.names if value(feature_vector, name) is not None}
        return [result(self.name, self.version, "RECON", feature_vector, score, evidence, reasons, ReconModelFeatures.names)]

    def health(self) -> dict[str, str]: return {"status": "running", "name": self.name}
