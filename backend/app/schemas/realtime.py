"""Realtime event envelope for browser consumers."""

from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel


class RealtimeEnvelope(BaseModel):
    event_type: Literal[
        "SYSTEM_STATUS", "INGEST_METRICS", "REPLAY_STATUS", "FEATURE_METRICS",
        "heartbeat", "alert", "system_status", "DETECTION_RESULT", "ALERT_CREATED", "ALERT_UPDATED",
    ]
    timestamp: datetime
    data: Any
