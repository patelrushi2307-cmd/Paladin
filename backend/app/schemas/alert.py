"""Central normalized alert contract."""

from datetime import datetime
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field


class Severity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ThreatClass(StrEnum):
    DDOS = "DDOS"
    C2_BEACON = "C2_BEACON"
    DGA_DNS_TUNNEL = "DGA_DNS_TUNNEL"
    ENCRYPTED_MALWARE = "ENCRYPTED_MALWARE"
    RECON = "RECON"
    DATA_EXFILTRATION = "DATA_EXFILTRATION"


class Alert(BaseModel):
    alert_id: str
    timestamp: datetime
    flow_id: str
    threat_class: ThreatClass
    severity: Severity
    confidence_score: float = Field(ge=0, le=1)
    source_ip: str
    destination_ip: str
    protocol: str
    evidence: dict[str, Any]
    detector: str
    model_version: str | None = None
    observation_window_ms: int = Field(ge=0)
    alert_type: str = "threat_observation"
    subtype: str | None = None
    scope: str = "FLOW"
    detector_version: str = "1.0.0"
    replay_session_id: str | None = None
    feature_schema_version: str = "1.0"
    created_at: datetime | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    occurrence_count: int = Field(default=1, ge=1)
    status: str = Field(default="NEW", pattern="^(NEW|ACKNOWLEDGED|RESOLVED)$")
    evidence_completeness: float = Field(default=0, ge=0, le=1)
    correlation_id: str | None = None
    why_flagged: str = "Observed behavior is consistent with a threat pattern."
