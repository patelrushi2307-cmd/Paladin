"""Verification of all 9 offline scenarios through the pipeline."""
from pathlib import Path
import asyncio, json, sys
sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from app.alerts.service import AlertService
from app.detectors.engine import DetectionEngine
from app.features.engine import FeatureEngine
from app.ingest.jsonl import JsonlTrafficSource
from app.repositories import AlertRepository
from tempfile import TemporaryDirectory

ROOT = Path(__file__).parents[1]
scenarios = [
    "01_normal", "02_ddos", "03_recon", "04_c2", "05_exfil",
    "06_dga", "07_dns_tunnel", "08_encrypted", "09_mixed_demo"
]

def run_scenario(name: str):
    source = JsonlTrafficSource(ROOT / "data" / "raw" / "scenarios" / f"{name}.jsonl")
    async def run():
        features = FeatureEngine()
        detectors = DetectionEngine()
        alerts = []
        with TemporaryDirectory() as d:
            repo = AlertRepository(f"sqlite:///{Path(d)}/e2e.db")
            service = AlertService(repo)
            await source.start()
            async for ev in source.stream():
                vec = features.process(ev)
                res = detectors.process(vec, {"source_ip": ev.src_ip, "destination_ip": ev.dst_ip, "protocol": ev.protocol})
                alt = service.process(res)
                if alt:
                    alerts.append(alt)
                if name == "09_mixed_demo" and ev.event_id in ("encrypted-0", "exfil-0", "dga-0"):
                    print(f"  [MIXED DEMO] {ev.event_id} -> Alert: {alt.threat_class.value if alt else 'NONE'}, Detectors: {[(r.threat_class, round(r.score, 2), r.detected) for r in res if r.detected]}")
            return len(features.recent), len(alerts), repo.count(), [a.threat_class.value for a in alerts]
    return asyncio.run(run())

if __name__ == "__main__":
    for name in scenarios:
        vecs, alts, db_cnt, threats = run_scenario(name)
        print(f"{name}: vectors={vecs}, alert_events={alts}, db_alerts={db_cnt}, classes={set(threats)}")
