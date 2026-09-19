"""Typed detector output and runtime status contracts."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class DetectorResult(BaseModel):
    detector: str
    detector_version: str
    threat_class: str
    detected: bool
    score: float = Field(ge=0, le=1)
    evidence: dict[str, Any] = Field(default_factory=dict)
    reasons: list[str] = Field(default_factory=list)
    scope: str
    model_score: float | None = Field(default=None, ge=0, le=1)
    model_available: bool = False
    model_version: str | None = None
    rule_score: float = Field(ge=0, le=1)
    features_used: list[str] = Field(default_factory=list)
    subtype: str | None = None
    evidence_completeness: float = Field(default=0, ge=0, le=1)
    applicability: str = "applicable"
    timestamp: datetime | None = None
    source_ip: str | None = None
    destination_ip: str | None = None
    protocol: str | None = None
    replay_session_id: str | None = None
    flow_id: str | None = None


class DetectorStatus(BaseModel):
    name: str
    enabled: bool
    status: str
    version: str
    scopes: list[str]
    model_available: bool = False
    results_emitted: int = 0
    errors: int = 0
    average_latency_ms: float = 0


class DetectionStatus(BaseModel):
    active_detectors: list[str]
    detector_count: int
    detector_results_emitted: int
    detector_results_dropped: int
    average_latency_ms: float
    errors: int
    detectors: list[DetectorStatus]
