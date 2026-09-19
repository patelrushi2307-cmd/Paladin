"""Transparent score fusion; confidence is not calibrated probability."""

from collections import defaultdict
from ..schemas.detector import DetectorResult
from ..schemas.fusion import UnifiedThreatAssessment


class ThreatScoreFusion:
    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = weights or defaultdict(lambda: 1.0)

    def assess(self, results: list[DetectorResult]) -> UnifiedThreatAssessment | None:
        applicable = [item for item in results if item.applicability == "applicable" and item.score > 0]
        if not applicable:
            return None
        primary = max(applicable, key=lambda item: item.score * self.weights[item.detector])
        weighted = [item.score * self.weights[item.detector] for item in applicable]
        score = min(1.0, max(weighted))
        agreement = min(1.0, (len(applicable) - 1) * 0.15)
        completeness = sum(item.evidence_completeness for item in applicable) / len(applicable)
        confidence = min(1.0, score * 0.65 + agreement + completeness * 0.2)
        severity = self._severity(primary.threat_class, score, primary.evidence)
        evidence = {"primary": [{"feature": key, "value": value} for key, value in list(primary.evidence.items())[:6]], "secondary": [item.model_dump(mode="json") for item in applicable[1:]], "derived": [{"feature": "evidence_completeness", "value": completeness}]}
        why = "; ".join(primary.reasons) or "Observed behavior is consistent with a threat pattern."
        return UnifiedThreatAssessment(threat_class=primary.threat_class, subtype=primary.subtype, score=score, confidence=confidence, severity=severity, evidence=evidence, detector_results=[item.detector for item in applicable], evidence_completeness=completeness, why_flagged=why)

    @staticmethod
    def _severity(threat_class: str, score: float, evidence: dict) -> str:
        impact = max((float(value) for value in evidence.values() if isinstance(value, (int, float))), default=0)
        if score >= .9 or (threat_class == "DDOS" and impact > 10000): return "CRITICAL"
        if score >= .75: return "HIGH"
        if score >= .5: return "MEDIUM"
        return "LOW"


fusion = ThreatScoreFusion()
