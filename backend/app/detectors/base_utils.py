"""Shared detector math and result helpers."""

from typing import Any
from ..schemas.detector import DetectorResult
from ..schemas.feature import FeatureVector


def value(vector: FeatureVector, name: str, default: Any = None) -> Any:
    return vector.values.get(name, default) if vector.availability.get(name, name in vector.values) else default


def clamp(number: float | None) -> float:
    if number is None:
        return 0.0
    return max(0.0, min(1.0, float(number)))


def threshold_score(number: Any, threshold: float, ceiling: float | None = None) -> float:
    if not isinstance(number, (int, float)) or threshold <= 0:
        return 0.0
    return clamp(float(number) / (ceiling or threshold * 2))


def result(detector: str, version: str, threat_class: str, vector: FeatureVector, score: float, evidence: dict[str, Any], reasons: list[str], features: list[str], model_score: float | None = None, subtype: str | None = None, applicability: str = "applicable") -> DetectorResult:
    available = sum(vector.availability.get(name, name in vector.values) for name in features)
    completeness = available / len(features) if features else 0.0
    return DetectorResult(detector=detector, detector_version=version, threat_class=threat_class, detected=score >= 0.5, score=clamp(score), evidence=evidence, reasons=reasons, scope=vector.scope, model_score=model_score, model_available=model_score is not None, model_version="future" if model_score is not None else None, rule_score=clamp(score), features_used=[name for name in features if vector.availability.get(name, name in vector.values)], subtype=subtype, evidence_completeness=completeness, applicability=applicability, timestamp=vector.timestamp)


def not_applicable(detector: str, version: str, threat_class: str, vector: FeatureVector, features: list[str]) -> DetectorResult:
    return result(detector, version, threat_class, vector, 0, {}, [], features, applicability="not_applicable")
