"""Feature vector contract with explicit scope and availability metadata."""

from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field


class FeatureVector(BaseModel):
    feature_id: str
    flow_id: str
    timestamp: datetime
    window_start: datetime | None = None
    window_end: datetime | None = None
    scope: Literal["FLOW", "SOURCE_WINDOW", "DESTINATION_WINDOW", "PAIR_WINDOW", "GLOBAL_WINDOW"] = "FLOW"
    source_type: str
    values: dict[str, Any] = Field(default_factory=dict)
    groups: dict[str, dict[str, Any]] = Field(default_factory=dict)
    availability: dict[str, bool] = Field(default_factory=dict)
    feature_schema_version: str = "1.0"

    @property
    def available(self) -> set[str]:
        return {name for name, available in self.availability.items() if available}


class FeatureStatus(BaseModel):
    feature_engine_status: str
    feature_vectors_per_sec: float
    feature_processing_latency_ms: float
    feature_processing_latency_max_ms: float
    feature_events_dropped: int
    feature_errors: int
    active_flow_state: int
    active_source_state: int
    active_pair_state: int
    recent_feature_vectors: int
    feature_queue_size: int
    feature_queue_maxsize: int
    window_count: int
