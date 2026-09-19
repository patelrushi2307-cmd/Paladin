"""Offline normalized FlowEvent load test for software throughput."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys, time
sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from app.schemas.flow import FlowEvent
from app.features.engine import FeatureEngine
from app.detectors.engine import DetectionEngine

def run(count: int = 1000):
    start = datetime(2026, 9, 19, tzinfo=timezone.utc); features = FeatureEngine(); detectors = DetectionEngine(); started = time.perf_counter()
    for index in range(count):
        event = FlowEvent(event_id=f"load-{index}", timestamp=start + timedelta(milliseconds=index), src_ip=f"10.50.{index // 250}.{index % 250 + 1}", dst_ip="10.60.0.1", src_port=40000 + index % 1000, dst_port=443, protocol="TCP", packets=4, bytes=400, duration=.01, direction="unknown", source_type="load")
        vector = features.process(event); detectors.process(vector, {"source_ip": event.src_ip, "destination_ip": event.dst_ip, "protocol": event.protocol})
    elapsed = max(time.perf_counter() - started, 1e-9); print({"events": count, "events_per_sec": count / elapsed, "detector_results": detectors.emitted, "errors": detectors.errors})
if __name__ == "__main__": run(int(sys.argv[1]) if len(sys.argv) > 1 else 1000)
