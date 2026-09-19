"""Score-fusion contracts."""

from typing import Any
from pydantic import BaseModel, Field


class UnifiedThreatAssessment(BaseModel):
    threat_class: str
    subtype: str | None = None
    score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    severity: str
    evidence: dict[str, Any]
    detector_results: list[str]
    evidence_completeness: float = Field(ge=0, le=1)
    why_flagged: str
