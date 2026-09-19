"""Normalized passive flow contract."""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class FlowEvent(BaseModel):
    """A flow normalized from a passive source; optional fields are metadata only."""

    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(min_length=1)
    timestamp: datetime
    src_ip: str
    dst_ip: str
    src_port: int | None = Field(default=None, ge=0, le=65535)
    dst_port: int | None = Field(default=None, ge=0, le=65535)
    protocol: str
    packets: int = Field(ge=0)
    bytes: int = Field(ge=0)
    duration: float = Field(ge=0)
    tcp_flags: str | None = None
    direction: Literal["inbound", "outbound", "internal_internal", "external_external", "unknown"] = "unknown"
    source_type: str
    dns_query: str | None = None
    dns_record_type: str | None = None
    tls_version: str | None = None
    tls_sni: str | None = None
    tls_ja3: str | None = None
    tls_ja3s: str | None = None
    tls_ja4: str | None = None
    alpn: str | None = None
    packet_size_summary: dict[str, float] | None = None
    packet_timing_summary: dict[str, float] | None = None
