"""Replay, ingestion lifecycle, and runtime metrics."""

import asyncio
from collections import deque
from datetime import datetime, timezone
import logging
from pathlib import Path
import time
from typing import Awaitable, Callable
from uuid import uuid4

from ..config import settings
from ..schemas.flow import FlowEvent
from ..schemas.ingest import IngestMetrics, IngestStatus, ReplayStatus
from .base import TrafficSource
from .event_bus import FlowEventBus
from .jsonl import JsonlTrafficSource
from .pcap import PcapTrafficSource

logger = logging.getLogger("paladin.ingest")
EventListener = Callable[[FlowEvent], Awaitable[None]]


class ReplayController:
    def __init__(self, on_event: Callable[[FlowEvent], Awaitable[None]]) -> None:
        self.on_event = on_event
        self.status_value = ReplayStatus()
        self.source: TrafficSource | None = None
        self._task: asyncio.Task[None] | None = None
        self._pause = asyncio.Event()
        self._pause.set()
        self._stop = asyncio.Event()
        self._mode = "realtime"

    async def start(self, source: TrafficSource, mode: str = "realtime", speed: float = 1, target_rate: float | None = None) -> ReplayStatus:
        if self._task and not self._task.done():
            raise RuntimeError("Replay is already running")
        self.source = source
        self._mode = mode
        self._pause.set()
        self._stop.clear()
        self.status_value = ReplayStatus(state="STARTING", replay_session_id=str(uuid4()), source_name=Path(source.health()["source"]).name, source_type=source.source_type, replay_speed=speed, target_flows_per_sec=target_rate, started_at=datetime.now(timezone.utc))
        self._task = asyncio.create_task(self._run(mode, speed, target_rate))
        return self.status_value

    async def _run(self, mode: str, speed: float, target_rate: float | None) -> None:
        assert self.source is not None
        previous_timestamp: datetime | None = None
        started = time.monotonic()
        try:
            await self.source.start()
            self.status_value.state = "RUNNING"
            async for event in self.source.stream():
                await self._pause.wait()
                if self._stop.is_set():
                    break
                if previous_timestamp is not None:
                    delay = max(0.0, (event.timestamp - previous_timestamp).total_seconds())
                    if mode == "accelerated":
                        delay /= speed
                    elif mode == "fixed_rate" and target_rate:
                        delay = 1 / target_rate
                    if delay:
                        await asyncio.sleep(min(delay, 5.0))
                previous_timestamp = event.timestamp
                await self.on_event(event)
                self.status_value.events_emitted += 1
                self.status_value.last_event_time = event.timestamp
                elapsed = max(time.monotonic() - started, 0.001)
                self.status_value.elapsed_time = elapsed
                self.status_value.actual_flows_per_sec = self.status_value.events_emitted / elapsed
            self.status_value.state = "STOPPING" if self._stop.is_set() else "COMPLETED"
            await self.source.stop()
        except asyncio.CancelledError:
            await self.source.stop()
            self.status_value.state = "STOPPING"
        except Exception as exc:
            self.status_value.state = "ERROR"
            self.status_value.error = str(exc)
            logger.exception("[INGEST] REPLAY_ERROR")

    async def pause(self) -> ReplayStatus:
        if self.status_value.state != "RUNNING":
            raise RuntimeError("Replay is not running")
        self._pause.clear()
        self.status_value.state = "PAUSED"
        return self.status_value

    async def resume(self) -> ReplayStatus:
        if self.status_value.state != "PAUSED":
            raise RuntimeError("Replay is not paused")
        self._pause.set()
        self.status_value.state = "RUNNING"
        return self.status_value

    async def stop(self) -> ReplayStatus:
        self._stop.set()
        self._pause.set()
        if self._task and not self._task.done():
            await self._task
        return self.status_value

    async def restart(self) -> ReplayStatus:
        if self.source is None:
            raise RuntimeError("No replay source loaded")
        source_type = self.status_value.source_type or "jsonl"
        path = Path(self.source.health()["source"])
        await self.stop()
        source = make_source(source_type, path)
        return await self.start(source, self._mode, self.status_value.replay_speed, self.status_value.target_flows_per_sec)

    def status(self) -> ReplayStatus:
        return self.status_value


class IngestManager:
    def __init__(self) -> None:
        self.bus = FlowEventBus(settings.event_queue_maxsize)
        self.controller = ReplayController(self._handle_event)
        self.listeners: list[EventListener] = []
        self.metrics = IngestMetrics(queue_maxsize=settings.event_queue_maxsize)
        self._recent_events: deque[tuple[float, int]] = deque()
        self._started_monotonic = 0.0

    def subscribe(self, listener: EventListener) -> None:
        self.listeners.append(listener)

    async def _handle_event(self, event: FlowEvent) -> None:
        received = time.monotonic()
        published = await self.bus.publish(event)
        if not published:
            self.metrics.events_dropped = self.bus.dropped
        self.metrics.flows_emitted += 1
        self.metrics.last_event_timestamp = event.timestamp
        self.metrics.active_flows = max(0, self.metrics.active_flows)
        self._recent_events.append((received, event.bytes))
        self._trim_recent(received)
        self._update_rates(received)
        for listener in list(self.listeners):
            await listener(event)

    def _trim_recent(self, now: float) -> None:
        cutoff = now - settings.metrics_window_seconds
        while self._recent_events and self._recent_events[0][0] < cutoff:
            self._recent_events.popleft()

    def _update_rates(self, now: float) -> None:
        self._trim_recent(now)
        window = max(settings.metrics_window_seconds, 1)
        self.metrics.flows_per_second = len(self._recent_events) / window
        self.metrics.bytes_per_second = sum(size for _, size in self._recent_events) / window
        self.metrics.throughput_mbps = self.metrics.bytes_per_second * 8 / 1_000_000

    async def start(self, source_type: str, path: Path, mode: str, speed: float, target_rate: float | None) -> ReplayStatus:
        self.metrics = IngestMetrics(started_at=datetime.now(timezone.utc), queue_maxsize=settings.event_queue_maxsize)
        self._started_monotonic = time.monotonic()
        source = make_source(source_type, path)
        return await self.controller.start(source, mode, speed, target_rate)

    async def stop(self) -> ReplayStatus:
        return await self.controller.stop()

    def status(self) -> IngestStatus:
        source = self.controller.source
        malformed = getattr(source, "malformed", 0) if source else 0
        unsupported = getattr(source, "unsupported", 0) if source else 0
        self.metrics.malformed_packets = malformed
        self.metrics.unsupported_packets = unsupported
        self.metrics.queue_size = self.bus.queue.qsize()
        self.metrics.events_dropped = self.bus.dropped
        return IngestStatus(state=self.controller.status().state, source_name=self.controller.status().source_name, source_type=self.controller.status().source_type, metrics=self.metrics)


def make_source(source_type: str, path: Path) -> TrafficSource:
    if source_type == "jsonl":
        return JsonlTrafficSource(path)
    if source_type == "pcap":
        return PcapTrafficSource(path, settings.flow_idle_timeout_seconds, settings.flow_max_duration_seconds)
    raise ValueError(f"Unsupported source type: {source_type}")


runtime = IngestManager()


async def feature_listener(event: FlowEvent) -> None:
    from ..features.engine import feature_engine
    from ..detectors.engine import detection_engine
    from ..dependencies import get_alert_service
    try:
        vector = feature_engine.process(event)
        detector_results = detection_engine.process(vector, {"source_type": event.source_type, "source_ip": event.src_ip, "destination_ip": event.dst_ip, "protocol": event.protocol, "replay_session_id": runtime.controller.status().replay_session_id})
        get_alert_service().process(detector_results)
    except Exception:
        logger.exception("[FEATURES] feature processing error event_id=%s", event.event_id)


runtime.subscribe(feature_listener)
