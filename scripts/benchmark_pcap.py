"""Benchmark the actual PCAP source through the full local pipeline."""
from pathlib import Path
import asyncio, json, sys, time
from tempfile import TemporaryDirectory
import numpy as np

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from app.alerts.service import AlertService
from app.detectors.engine import DetectionEngine
from app.features.engine import FeatureEngine
from app.ingest.pcap import PcapTrafficSource
from app.repositories import AlertRepository

def get_process_memory_mb() -> float:
    try:
        import psutil
        return round(psutil.Process().memory_info().rss / (1024 * 1024), 2)
    except Exception:
        return 0.0


async def run(pcap_path: Path | None = None) -> dict:
    target_path = pcap_path or (Path(__file__).parents[1] / "data" / "raw" / "synthetic_fixture.pcap")
    source = PcapTrafficSource(target_path, idle_timeout=0.01, max_duration=300)
    features = FeatureEngine()
    detectors = DetectionEngine()
    
    feature_latencies = []
    detector_latencies = []
    alert_latencies = []
    e2e_latencies = []
    
    source_count = 0
    result_count = 0
    alert_count = 0
    
    mem_before = get_process_memory_mb()
    started = time.perf_counter()
    
    with TemporaryDirectory() as directory:
        service = AlertService(AlertRepository(f"sqlite:///{Path(directory) / 'pcap.db'}"))
        await source.start()
        async for event in source.stream():
            source_count += 1
            flow_start = time.perf_counter()
            
            t0 = time.perf_counter()
            vector = features.process(event)
            t1 = time.perf_counter()
            
            results = detectors.process(vector, {
                "source_ip": event.src_ip,
                "destination_ip": event.dst_ip,
                "protocol": event.protocol
            })
            t2 = time.perf_counter()
            result_count += len(results)
            
            alert = service.process(results)
            t3 = time.perf_counter()
            if alert is not None:
                alert_count += 1
                
            flow_end = time.perf_counter()
            
            feature_latencies.append((t1 - t0) * 1000)
            detector_latencies.append((t2 - t1) * 1000)
            alert_latencies.append((t3 - t2) * 1000)
            e2e_latencies.append((flow_end - flow_start) * 1000)
            
        elapsed = max(time.perf_counter() - started, 1e-9)
        
    mem_after = get_process_memory_mb()
    
    def stats(arr: list[float]) -> dict:
        if not arr:
            return {"mean": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0}
        nparr = np.asarray(arr, dtype=float)
        return {
            "mean": float(np.mean(nparr)),
            "p50": float(np.percentile(nparr, 50)),
            "p95": float(np.percentile(nparr, 95)),
            "p99": float(np.percentile(nparr, 99)),
        }
        
    res = {
        "input": str(target_path),
        "packets": source.aggregator.packets_seen,
        "flows": source_count,
        "feature_vectors": len(features.recent),
        "detector_results": result_count,
        "alerts": alert_count,
        "elapsed_seconds": elapsed,
        "packets_per_sec": source.aggregator.packets_seen / elapsed,
        "flows_per_sec": source_count / elapsed,
        "events_per_sec": source_count / elapsed,
        "mbps": source.aggregator.bytes_seen * 8 / elapsed / 1_000_000,
        "latency_ms": {
            "feature": stats(feature_latencies),
            "detector": stats(detector_latencies),
            "alert": stats(alert_latencies),
            "end_to_end": stats(e2e_latencies),
        },
        "feature_latency_ms": float(np.mean(feature_latencies)) if feature_latencies else 0.0,
        "detector_latency_ms": detectors.status().average_latency_ms,
        "alert_latency_ms": float(np.mean(alert_latencies)) if alert_latencies else 0.0,
        "end_to_end_latency_ms": float(np.mean(e2e_latencies)) if e2e_latencies else 0.0,
        "drops": source.aggregator.packets_seen - source_count if source.aggregator.packets_seen < source_count else 0,
        "errors": detectors.errors + features.errors,
        "queue_depth": features.feature_queue.qsize(),
        "malformed_packets": source.malformed,
        "unsupported_packets": source.unsupported,
        "detector_errors": detectors.errors,
        "memory_mb": {
            "start": mem_before,
            "peak": max(mem_before, mem_after),
            "end": mem_after
        }
    }
    print(json.dumps(res, indent=2))
    return res

if __name__ == "__main__":
    pcap_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    asyncio.run(run(pcap_arg))
