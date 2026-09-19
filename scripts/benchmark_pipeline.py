"""Measure local JSONL -> feature -> six detectors -> alert processing."""
from pathlib import Path
import asyncio, sys, time
sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from app.features.engine import FeatureEngine
from app.detectors.engine import DetectionEngine
from app.alerts.service import AlertService
from app.repositories import AlertRepository
from app.ingest.jsonl import JsonlTrafficSource
from tempfile import TemporaryDirectory
path = Path(__file__).parents[1] / "data" / "raw" / "scenarios" / "09_mixed_demo.jsonl"

async def run():
    source = JsonlTrafficSource(path); await source.start(); features = FeatureEngine(); detectors = DetectionEngine(); started = time.perf_counter(); flow_count = 0; result_count = 0; alert_count = 0
    with TemporaryDirectory() as directory:
        alerts = AlertService(AlertRepository(f"sqlite:///{Path(directory) / 'benchmark.db'}"))
        async for event in source.stream():
            flow_count += 1; vector = features.process(event); results = detectors.process(vector, {"source_ip": event.src_ip, "destination_ip": event.dst_ip, "protocol": event.protocol}); result_count += len(results); alert_count += alerts.process(results) is not None
        elapsed = max(time.perf_counter() - started, 1e-9)
    print({"input": str(path), "flows": flow_count, "feature_vectors": len(features.recent), "detector_results": result_count, "alerts": alert_count, "pipeline_events_per_sec": flow_count / elapsed, "feature_latency_ms": features.status()["feature_processing_latency_ms"], "detector_latency_ms": detectors.status().average_latency_ms, "errors": detectors.errors})

asyncio.run(run())
