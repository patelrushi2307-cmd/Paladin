"""Run the real Paladin pipeline on 09_mixed_demo.jsonl to populate data/paladin.db."""
import asyncio
import os
import sys
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from backend.app.alerts.service import AlertService
from backend.app.config import settings
from backend.app.detectors.engine import DetectionEngine
from backend.app.features.engine import FeatureEngine
from backend.app.ingest.jsonl import JsonlTrafficSource
from backend.app.repositories import AlertRepository


async def main():
    scenario_path = PROJECT_ROOT / "data" / "raw" / "scenarios" / "09_mixed_demo.jsonl"
    print(f"[*] Processing real network flows from: {scenario_path}")
    source = JsonlTrafficSource(scenario_path)

    features = FeatureEngine()
    detectors = DetectionEngine()
    repo = AlertRepository(settings.database_url)
    service = AlertService(repo)

    count = 0
    alert_count = 0

    await source.start()
    async for event in source.stream():
        count += 1
        vector = features.process(event)
        results = detectors.process(
            vector,
            {
                "source_ip": event.src_ip,
                "destination_ip": event.dst_ip,
                "protocol": event.protocol,
            },
        )
        alert = service.process(results)
        if alert:
            alert_count += 1

    print(f"[+] Successfully processed {count} flows into Paladin pipeline.")
    print(f"[+] Generated {alert_count} real threat alerts in {settings.database_url}")
    print(f"[+] Total alerts in DB: {repo.count()}")
    repo.close()


if __name__ == "__main__":
    asyncio.run(main())
