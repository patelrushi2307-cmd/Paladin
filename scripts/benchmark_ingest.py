"""Small local benchmark for normalized JSONL -> FlowEvent -> FeatureVector."""

import asyncio
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from app.features.engine import FeatureEngine
from app.ingest.jsonl import JsonlTrafficSource


async def main() -> None:
    path = Path(__file__).parents[1] / "data" / "raw" / "benign_flows.jsonl"
    source = JsonlTrafficSource(path)
    engine = FeatureEngine()
    count = 0
    started = time.perf_counter()
    await source.start()
    async for event in source.stream():
        engine.process(event)
        count += 1
    elapsed = max(time.perf_counter() - started, 1e-9)
    print("INGEST BENCHMARK")
    print(f"Input: {path}")
    print(f"FlowEvents processed: {count}")
    print(f"Feature vectors emitted: {engine.status()['recent_feature_vectors']}")
    print(f"Average processing rate: {count / elapsed:.2f} events/sec")
    print(f"Average feature latency: {engine.status()['feature_processing_latency_ms']:.4f} ms")
    print(f"Dropped features: {engine.status()['feature_events_dropped']}")
    print(f"Malformed events: {source.malformed}")


if __name__ == "__main__":
    asyncio.run(main())
