"""Measure local detector throughput on one representative FeatureVector."""
from datetime import datetime, timezone
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from app.detectors.engine import DetectionEngine
from app.schemas.feature import FeatureVector

vector = FeatureVector(feature_id="benchmark", flow_id="benchmark", timestamp=datetime.now(timezone.utc), scope="SOURCE_WINDOW", source_type="benchmark", values={"packets_per_sec": 1000, "bytes_per_sec": 1_000_000, "flows_per_sec": 100, "unique_src_count": 50, "source_ip_entropy": 4, "destination_concentration": .8, "syn_ratio": .8, "ack_ratio": .2, "udp_ratio": .1, "burst_packets_per_sec": 1000, "burst_bytes_per_sec": 1_000_000, "fanout_hosts": 50, "fanout_ports": 20, "scan_velocity": 10, "unique_dst_hosts": 50, "unique_dst_ports": 20, "destination_ip_entropy": 4, "observation_count": 8, "iat_mean": 30, "iat_std": .2, "iat_cv": .01, "periodicity_score": .98, "repeated_destination_ratio": .9, "flow_duration": 120, "bytes_total": 10_000_000, "packets_total": 1000, "direction_class": "OUTBOUND", "outbound_bytes": 9_000_000, "inbound_bytes": 100_000, "outbound_rate": 1_000_000, "outbound_inbound_ratio": 90, "tls_metadata_available": True, "protocol": "TLS", "tls_ja4": "benchmark", "packet_size_std": 250}, availability={})

engine = DetectionEngine()
iterations = 1000
started = time.perf_counter()
for _ in range(iterations):
    engine.process(vector)
elapsed = time.perf_counter() - started
print("DETECTOR BENCHMARK")
print(f"Vectors: {iterations}")
print(f"Detector results: {engine.emitted}")
print(f"Throughput: {iterations / elapsed:.2f} vectors/sec")
print(f"Average engine latency: {elapsed * 1000 / iterations:.4f} ms")
print(f"Errors: {engine.errors}")
for detector in engine.status().detectors:
    print(f"{detector.name}: {detector.average_latency_ms:.4f} ms")
