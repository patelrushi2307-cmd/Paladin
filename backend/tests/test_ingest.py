import asyncio
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.ingest.event_bus import FlowEventBus
from app.ingest.flow_aggregator import FlowAggregator
from app.ingest.jsonl import JsonlTrafficSource
from app.main import app
from app.system_contract import ACTIVE_PROBING, INLINE_MITIGATION, ONE_WAY_ONLY, PAYLOAD_DECRYPTION


def event_payload(event_id: str = "one") -> dict[str, object]:
    return {"event_id": event_id, "timestamp": "2026-09-19T10:00:00Z", "src_ip": "10.0.0.1", "dst_ip": "10.0.0.2", "src_port": 50000, "dst_port": 443, "protocol": "TCP", "packets": 2, "bytes": 100, "duration": 0.2, "source_type": "jsonl"}


def test_jsonl_source_reads_valid_lines_and_skips_bad(tmp_path: Path) -> None:
    path = tmp_path / "flows.jsonl"
    path.write_text(json.dumps(event_payload()) + "\nnot-json\n", encoding="utf-8")
    source = JsonlTrafficSource(path)
    async def collect():
        await source.start()
        return [event async for event in source.stream()]
    events = asyncio.run(collect())
    assert len(events) == 1
    assert source.malformed == 1


def test_flow_aggregator_finalizes_idle_flow() -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    aggregator = FlowAggregator(idle_timeout=2, max_duration=300)
    assert aggregator.add_packet(timestamp=start, src_ip="10.0.0.1", dst_ip="10.0.0.2", src_port=1, dst_port=2, protocol="TCP", packet_bytes=50) == []
    finalized = aggregator.add_packet(timestamp=start + timedelta(seconds=3), src_ip="10.0.0.3", dst_ip="10.0.0.4", src_port=3, dst_port=4, protocol="UDP", packet_bytes=70)
    assert finalized[0].packets == 1
    assert finalized[0].bytes == 50

def test_bounded_queue_counts_drops() -> None:
    bus = FlowEventBus(maxsize=1)
    from app.schemas.flow import FlowEvent
    event = FlowEvent.model_validate(event_payload())
    async def publish():
        return await bus.publish(event, timeout=0.01), await bus.publish(event, timeout=0.01)
    first, second = asyncio.run(publish())
    assert first is True
    assert second is False
    assert bus.dropped == 1


def test_ingest_api_and_security_contract() -> None:
    client = TestClient(app)
    assert client.get("/api/ingest/status").status_code == 200
    assert client.get("/api/ingest/metrics").status_code == 200
    assert client.get("/api/replay/status").status_code == 200
    assert client.get("/api/replay/sources").status_code == 200
    assert client.post("/api/replay/start", json={"source_type": "jsonl", "source_path": "../outside.jsonl"}).status_code == 400
    assert ONE_WAY_ONLY is True
    assert PAYLOAD_DECRYPTION is False
    assert ACTIVE_PROBING is False
    assert INLINE_MITIGATION is False
