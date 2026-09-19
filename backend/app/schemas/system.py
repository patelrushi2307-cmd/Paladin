"""System and realtime contracts."""

from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel
from .alert import Alert


class SystemStatus(BaseModel):
    service_status: Literal["healthy", "degraded", "offline"] = "healthy"
    ingest_status: Literal["ready", "running", "stopped"] = "ready"
    ingest_mode: str = "passive"
    receive_only: bool = True
    payload_decryption: bool = False
    return_path: bool = False
    active_detectors: list[str] = []
    flows_per_second: float = 0
    throughput_mbps: float = 0
    alerts_total: int = 0
    last_event_timestamp: datetime | None = None


class RealtimeEvent(BaseModel):
    event_type: Literal["heartbeat", "alert", "system_status"]
    timestamp: datetime
    payload: SystemStatus | Alert | dict[str, Any]
