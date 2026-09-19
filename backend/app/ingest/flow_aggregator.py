"""Bounded deterministic packet-to-flow aggregation."""

from dataclasses import dataclass, field
from datetime import datetime
import hashlib

from ..schemas.flow import FlowEvent


@dataclass
class MutableFlow:
    src_ip: str
    dst_ip: str
    src_port: int | None
    dst_port: int | None
    protocol: str
    first_seen: datetime
    last_seen: datetime
    packets: int = 0
    bytes: int = 0
    flags: set[str] = field(default_factory=set)
    packet_sizes: list[int] = field(default_factory=list)
    packet_times: list[datetime] = field(default_factory=list)

    @property
    def key(self) -> tuple[object, ...]:
        return (self.src_ip, self.dst_ip, self.src_port, self.dst_port, self.protocol)

    def add(self, timestamp: datetime, packet_bytes: int, tcp_flags: str | None) -> None:
        self.last_seen = max(self.last_seen, timestamp)
        self.packets += 1
        self.bytes += max(0, packet_bytes)
        if tcp_flags:
            self.flags.update(tcp_flags.upper().replace(",", " ").split())
        if len(self.packet_sizes) < 100:
            self.packet_sizes.append(max(0, packet_bytes))
            self.packet_times.append(timestamp)

    def event(self, source_type: str) -> FlowEvent:
        flow_id = hashlib.sha256(repr(self.key).encode("utf-8")).hexdigest()[:24]
        duration = max(0.0, (self.last_seen - self.first_seen).total_seconds())
        return FlowEvent(
            event_id=flow_id,
            timestamp=self.first_seen,
            src_ip=self.src_ip,
            dst_ip=self.dst_ip,
            src_port=self.src_port,
            dst_port=self.dst_port,
            protocol=self.protocol,
            packets=self.packets,
            bytes=self.bytes,
            duration=duration,
            tcp_flags=" ".join(sorted(self.flags)) or None,
            direction="unknown",
            source_type=source_type,
            packet_size_summary={"min": float(min(self.packet_sizes)), "max": float(max(self.packet_sizes)), "mean": sum(self.packet_sizes) / len(self.packet_sizes)} if self.packet_sizes else None,
            packet_timing_summary={"first": self.packet_times[0].timestamp(), "last": self.packet_times[-1].timestamp()} if self.packet_times else None,
        )


class FlowAggregator:
    def __init__(self, idle_timeout: float = 30, max_duration: float = 300, source_type: str = "pcap") -> None:
        self.idle_timeout = idle_timeout
        self.max_duration = max_duration
        self.source_type = source_type
        self.active: dict[tuple[object, ...], MutableFlow] = {}
        self.packets_seen = 0
        self.bytes_seen = 0

    def add_packet(self, *, timestamp: datetime, src_ip: str, dst_ip: str, src_port: int | None, dst_port: int | None, protocol: str, packet_bytes: int, tcp_flags: str | None = None) -> list[FlowEvent]:
        finalized = self.expire(timestamp)
        key = (src_ip, dst_ip, src_port, dst_port, protocol)
        flow = self.active.get(key)
        if flow is None:
            flow = MutableFlow(src_ip, dst_ip, src_port, dst_port, protocol, timestamp, timestamp)
            self.active[key] = flow
        flow.add(timestamp, packet_bytes, tcp_flags)
        self.packets_seen += 1
        self.bytes_seen += max(0, packet_bytes)
        return finalized

    def expire(self, now: datetime) -> list[FlowEvent]:
        finalized: list[FlowEvent] = []
        for key, flow in list(self.active.items()):
            idle = (now - flow.last_seen).total_seconds()
            age = (now - flow.first_seen).total_seconds()
            if idle >= self.idle_timeout or age >= self.max_duration:
                finalized.append(flow.event(self.source_type))
                del self.active[key]
        return finalized

    def flush(self) -> list[FlowEvent]:
        finalized = [flow.event(self.source_type) for flow in self.active.values()]
        self.active.clear()
        return finalized
