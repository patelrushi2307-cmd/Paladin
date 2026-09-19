"""Typed ingestion and metrics contracts."""

from datetime import datetime
from pydantic import BaseModel, Field


class IngestMetrics(BaseModel):
    packets_seen: int = 0
    flows_emitted: int = 0
    flows_per_second: float = 0
    bytes_per_second: float = 0
    throughput_mbps: float = 0
    active_flows: int = 0
    events_dropped: int = 0
    malformed_packets: int = 0
    unsupported_packets: int = 0
    ingest_latency_ms: float = 0
    queue_size: int = 0
    queue_maxsize: int = 10000
    started_at: datetime | None = None
    last_event_timestamp: datetime | None = None


class IngestStatus(BaseModel):
    state: str = "IDLE"
    source_name: str | None = None
    source_type: str | None = None
    metrics: IngestMetrics
    error: str | None = None


class ReplaySource(BaseModel):
    name: str
    source_type: str
    size_bytes: int
    path: str


class ReplaySourcesResponse(BaseModel):
    sources: list[ReplaySource]


class ReplayLoadRequest(BaseModel):
    source_type: str = Field(pattern="^(pcap|jsonl)$")
    source_path: str = Field(min_length=1)


class ReplayStartRequest(ReplayLoadRequest):
    mode: str = Field(default="realtime", pattern="^(realtime|accelerated|fixed_rate)$")
    speed_multiplier: float = Field(default=1.0, gt=0)
    target_flows_per_sec: float | None = Field(default=None, gt=0)


class ReplayStatus(BaseModel):
    state: str = "IDLE"
    replay_session_id: str | None = None
    source_name: str | None = None
    source_type: str | None = None
    total_estimated_events: int | None = None
    events_emitted: int = 0
    elapsed_time: float = 0
    replay_speed: float = 1
    target_flows_per_sec: float | None = None
    actual_flows_per_sec: float = 0
    started_at: datetime | None = None
    last_event_time: datetime | None = None
    error: str | None = None
