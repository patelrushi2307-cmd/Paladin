"""Bounded event-time state for source, destination, pair, and windows."""

from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from ..schemas.flow import FlowEvent


@dataclass
class BehaviorState:
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    flows: int = 0
    packets: int = 0
    bytes: int = 0
    destinations: deque[str] = field(default_factory=deque)
    destination_ports: deque[int] = field(default_factory=deque)
    sources: deque[str] = field(default_factory=deque)
    source_ports: deque[int] = field(default_factory=deque)
    timestamps: deque[datetime] = field(default_factory=deque)
    protocols: Counter[str] = field(default_factory=Counter)
    dns_queries: deque[str] = field(default_factory=deque)
    tls_fingerprints: deque[str] = field(default_factory=deque)

    def update(self, event: FlowEvent, max_items: int) -> None:
        self.first_seen = self.first_seen or event.timestamp
        self.last_seen = max(self.last_seen or event.timestamp, event.timestamp)
        self.flows += 1
        self.packets += event.packets
        self.bytes += event.bytes
        for collection, value in ((self.destinations, event.dst_ip), (self.destination_ports, event.dst_port), (self.sources, event.src_ip), (self.source_ports, event.src_port), (self.dns_queries, event.dns_query), (self.tls_fingerprints, event.tls_ja4 or event.tls_ja3)):
            if value is not None:
                collection.append(value)
                while len(collection) > max_items:
                    collection.popleft()
        self.timestamps.append(event.timestamp)
        while len(self.timestamps) > max_items:
            self.timestamps.popleft()
        self.protocols[event.protocol.upper()] += 1


class StreamingStateManager:
    def __init__(self, ttl_seconds: float = 300, max_items: int = 100) -> None:
        self.ttl = timedelta(seconds=ttl_seconds)
        self.max_items = max_items
        self.flow_states: dict[str, BehaviorState] = {}
        self.source_states: dict[str, BehaviorState] = {}
        self.destination_states: dict[str, BehaviorState] = {}
        self.pair_states: dict[tuple[str, str], BehaviorState] = {}
        self.events: deque[FlowEvent] = deque(maxlen=max_items * 20)
        self.feature_errors = 0
        self.invalid_ip_events = 0

    def update(self, event: FlowEvent) -> None:
        self.expire(event.timestamp)
        self.events.append(event)
        self.flow_states.setdefault(event.event_id, BehaviorState()).update(event, self.max_items)
        self.source_states.setdefault(event.src_ip, BehaviorState()).update(event, self.max_items)
        self.destination_states.setdefault(event.dst_ip, BehaviorState()).update(event, self.max_items)
        self.pair_states.setdefault((event.src_ip, event.dst_ip), BehaviorState()).update(event, self.max_items)

    def expire(self, now: datetime) -> None:
        for mapping in (self.flow_states, self.source_states, self.destination_states, self.pair_states):
            for key, state in list(mapping.items()):
                if state.last_seen and now - state.last_seen > self.ttl:
                    del mapping[key]
        cutoff = now - self.ttl
        while self.events and self.events[0].timestamp < cutoff:
            self.events.popleft()

    def window_events(self, end: datetime, seconds: float) -> list[FlowEvent]:
        start = end - timedelta(seconds=seconds)
        return [event for event in self.events if start <= event.timestamp <= end]

    def counts(self) -> dict[str, int]:
        return {"active_flow_state": len(self.flow_states), "active_source_state": len(self.source_states), "active_pair_state": len(self.pair_states)}


class WindowManager:
    def __init__(self, windows: tuple[int, ...] = (1, 5, 30, 60)) -> None:
        self.windows = windows

    def bounds(self, end: datetime, seconds: int) -> tuple[datetime, datetime]:
        return end - timedelta(seconds=seconds), end
