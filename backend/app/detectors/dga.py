"""Passive lexical DGA and DNS tunnelling indicators."""

from typing import Any
from .base import ThreatDetector
from .base_utils import not_applicable, result, value, clamp
from ..schemas.detector import DetectorResult
from ..schemas.feature import FeatureVector


class DgaModelFeatures:
    names = ["dns_query_entropy", "dns_query_length", "digit_ratio", "character_diversity", "label_count", "subdomain_depth", "ngram_score"]


class DgaDnsDetector(ThreatDetector):
    name = "dga_dns"
    version = "1.0.0"
    scopes = ("FLOW", "SOURCE_WINDOW", "GLOBAL_WINDOW")

    def initialize(self) -> None: pass

    def detect(self, feature_vector: FeatureVector, context: dict[str, Any]) -> list[DetectorResult]:
        if not self.supports_scope(feature_vector.scope): return []
        dns_available = any(feature_vector.availability.get(name, False) for name in ("dns_query_length", "dns_query_entropy", "label_count"))
        if not dns_available: return [not_applicable(self.name, self.version, "DGA_DNS_TUNNEL", feature_vector, DgaModelFeatures.names)]
        entropy = value(feature_vector, "dns_query_entropy", 0) or 0
        length = value(feature_vector, "dns_query_length", 0) or 0
        digit = value(feature_vector, "digit_ratio", 0) or 0
        diversity = value(feature_vector, "character_diversity", 0) or 0
        labels = value(feature_vector, "label_count", 0) or 0
        ngram = value(feature_vector, "ngram_score")
        dga_score = clamp(min(1, float(entropy) / 5) * .3 + min(1, float(length) / 40) * .2 + min(1, float(digit) * 2) * .2 + min(1, float(diversity) * 1.5) * .2 + (float(ngram) * .1 if isinstance(ngram, (int, float)) else 0))
        tunnel_score = clamp(min(1, float(length) / 50) * .3 + min(1, float(entropy) / 5) * .2 + min(1, float(value(feature_vector, "subdomain_depth", 0) or 0) / 4) * .15 + (1 if value(feature_vector, "txt_record") is True else 0) * .2 + min(1, float(value(feature_vector, "unique_dns_query_ratio", 0) or 0)) * .15)
        subtype = "DGA_LIKE" if dga_score >= tunnel_score else "DNS_TUNNEL_LIKE"
        score = max(dga_score, tunnel_score)
        reasons = []
        if dga_score >= .5: reasons.extend(["lexical_entropy_anomaly", "unusual_domain_structure"])
        if tunnel_score >= .5: reasons.extend(["long_high_entropy_query", "dns_tunnel_like_behavior"])
        evidence = {name: value(feature_vector, name) for name in DgaModelFeatures.names}
        evidence.update({"dga_score": dga_score, "dns_tunnel_score": tunnel_score})
        return [result(self.name, self.version, "DGA_DNS_TUNNEL", feature_vector, score, evidence, reasons, DgaModelFeatures.names, subtype=subtype)]

    def health(self) -> dict[str, str]: return {"status": "running", "name": self.name}
