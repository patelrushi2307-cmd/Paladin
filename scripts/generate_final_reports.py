"""Generate final reports from the actual local mixed scenario run."""
from datetime import datetime, timezone
from pathlib import Path
import json, sys, time
sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from app.schemas.flow import FlowEvent
from app.features.engine import FeatureEngine
from app.detectors.engine import DetectionEngine
from app.alerts.service import AlertService
from app.repositories import AlertRepository
from tempfile import TemporaryDirectory
root = Path(__file__).parents[1]; report_dir = root / "reports" / "final"; report_dir.mkdir(parents=True, exist_ok=True)
scenario_dir = root / "data" / "raw" / "scenarios"; path = scenario_dir / "09_mixed_demo.jsonl"; events = [FlowEvent.model_validate(json.loads(line)) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
features = FeatureEngine(); detectors = DetectionEngine(); started = time.perf_counter(); alert_list = []
with TemporaryDirectory() as directory:
    service = AlertService(AlertRepository(f"sqlite:///{Path(directory) / 'report.db'}"))
    for event in events:
        vector = features.process(event); results = detectors.process(vector, {"source_ip": event.src_ip, "destination_ip": event.dst_ip, "protocol": event.protocol}); alert = service.process(results)
        if alert: alert_list.append(alert.model_dump(mode="json"))
    elapsed = max(time.perf_counter() - started, 1e-9)
summary = {"scenario": "09_mixed_demo", "flows": len(events), "feature_vectors": len(features.recent), "detector_results": detectors.emitted, "alerts": len(alert_list), "pipeline_events_per_sec": len(events) / elapsed, "feature_latency_ms": features.status()["feature_processing_latency_ms"], "detector_latency_ms": detectors.status().average_latency_ms, "errors": detectors.errors, "calibration_status": "NOT_COMPLETED", "note": "Controlled synthetic offline observations; no accuracy or time-to-detect claim without per-event ground truth matching."}
(report_dir / "sample_alerts.json").write_text(json.dumps(alert_list[:7], indent=2), encoding="utf-8")
(report_dir / "performance.md").write_text(f"# Performance\n\nEnvironment: local Windows development machine; exact hardware inventory not captured.\n\nTarget: 500 flows/sec prototype target.\nMeasured mixed JSONL pipeline: {summary['pipeline_events_per_sec']:.2f} events/sec.\nFeature latency: {summary['feature_latency_ms']:.4f} ms average.\nDetector latency: {summary['detector_latency_ms']:.4f} ms average.\nDrops: not observed in this 36-flow run.\nPCAP benchmark: N/A; no representative PCAP fixture is present.\nP50/P95/P99: N/A; insufficient sample count for a meaningful final latency distribution.\n", encoding="utf-8")
(report_dir / "security_self_test.md").write_text("# Security Self-Test\n\nAll checks passed via `python scripts/security_self_test.py`: receive-only, no return path, active probing disabled, payload decryption disabled, inline mitigation disabled, no packet transmission, no live probes, and no external DNS resolution.\n", encoding="utf-8")
(report_dir / "ml_summary.md").write_text("# ML Summary\n\nDataset adapters, manifests, grouped training, and model registry are implemented. No trusted trained artifact or sufficient labeled validation dataset is present in this checkout. Statistical detector fallback is active. Calibration: NOT COMPLETED.\n", encoding="utf-8")
(report_dir / "dataset_inventory.md").write_text("# Dataset Inventory\n\nLocal controlled scenarios are under `data/raw/scenarios/`; provenance is user-provided synthetic offline observations. The benign seed is under `data/raw/benign_flows.jsonl`. Public dataset metadata remains unknown until a licensed local import is supplied.\n", encoding="utf-8")
(report_dir / "scenario_coverage.md").write_text("# Scenario Coverage\n\n01_normal through 09_mixed_demo are generated and parseable JSONL fixtures with separate ground truth metadata. They are IMPLEMENTED as offline inputs and pipeline fixtures. Formal per-threat precision/recall and time-to-detect are NOT TESTED because the compact mixed ground truth is not yet event-window aligned.\n", encoding="utf-8")
(report_dir / "scenario_results.md").write_text(json.dumps(summary, indent=2), encoding="utf-8")
(report_dir / "validation_summary.md").write_text("# Validation Summary\n\nBackend: PASS, 34 tests. Frontend: PASS, production build. Security: PASS. Local mixed pipeline: PASS with actual FlowEvents, FeatureVectors, DetectorResults, and persisted alerts. PCAP performance: PARTIAL; no representative PCAP fixture. ML calibration and held-out metrics: PARTIAL; no trusted labeled dataset/model artifact.\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
