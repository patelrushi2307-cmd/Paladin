import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
from app.alerts.service import AlertService
from app.detectors.engine import DetectionEngine
from app.features.engine import FeatureEngine
from app.ingest.jsonl import JsonlTrafficSource
from app.ingest.pcap import PcapTrafficSource
from app.repositories import AlertRepository

ROOT = Path(__file__).parents[2]


def run_pipeline(source):
    async def execute():
        features = FeatureEngine(); detectors = DetectionEngine(); count = 0; result_count = 0; alert_count = 0
        with TemporaryDirectory() as directory:
            repo = AlertRepository(f"sqlite:///{Path(directory) / 'e2e.db'}")
            service = AlertService(repo)
            try:
                await source.start()
                async for event in source.stream():
                    count += 1; vector = features.process(event); results = detectors.process(vector, {"source_ip": event.src_ip, "destination_ip": event.dst_ip, "protocol": event.protocol}); result_count += len(results); alert_count += service.process(results) is not None
            finally:
                repo.close()
        return count, len(features.recent), result_count, alert_count
    return asyncio.run(execute())


def test_jsonl_full_pipeline():
    source = JsonlTrafficSource(ROOT / "data" / "raw" / "scenarios" / "09_mixed_demo.jsonl")
    flows, vectors, results, alerts = run_pipeline(source)
    assert (flows, vectors) == (36, 36)
    assert results > 0 and alerts > 0


def test_pcap_full_pipeline():
    source = PcapTrafficSource(ROOT / "data" / "raw" / "synthetic_fixture.pcap", idle_timeout=.01)
    flows, vectors, results, alerts = run_pipeline(source)
    assert flows == 22 and vectors == 22
    assert results == 132 and alerts > 0
    assert source.malformed == 0 and source.unsupported == 0


def test_normal_scenario():
    source = JsonlTrafficSource(ROOT / "data" / "raw" / "scenarios" / "01_normal.jsonl")
    flows, vectors, results, alerts = run_pipeline(source)
    assert flows == 5 and vectors == 5
    assert alerts == 0


def test_ddos_scenario():
    source = JsonlTrafficSource(ROOT / "data" / "raw" / "scenarios" / "02_ddos.jsonl")
    flows, vectors, results, alerts = run_pipeline(source)
    assert flows == 8 and vectors == 8
    assert alerts > 0


def test_recon_scenario():
    source = JsonlTrafficSource(ROOT / "data" / "raw" / "scenarios" / "03_recon.jsonl")
    flows, vectors, results, alerts = run_pipeline(source)
    assert flows == 8 and vectors == 8
    assert alerts > 0


def test_c2_scenario():
    source = JsonlTrafficSource(ROOT / "data" / "raw" / "scenarios" / "04_c2.jsonl")
    flows, vectors, results, alerts = run_pipeline(source)
    assert flows == 6 and vectors == 6
    assert alerts > 0


def test_exfil_scenario():
    source = JsonlTrafficSource(ROOT / "data" / "raw" / "scenarios" / "05_exfil.jsonl")
    flows, vectors, results, alerts = run_pipeline(source)
    assert flows == 1 and vectors == 1
    assert alerts == 1


def test_dga_scenario():
    source = JsonlTrafficSource(ROOT / "data" / "raw" / "scenarios" / "06_dga.jsonl")
    flows, vectors, results, alerts = run_pipeline(source)
    assert flows == 1 and vectors == 1
    assert alerts == 1


def test_dns_tunnel_scenario():
    source = JsonlTrafficSource(ROOT / "data" / "raw" / "scenarios" / "07_dns_tunnel.jsonl")
    flows, vectors, results, alerts = run_pipeline(source)
    assert flows == 6 and vectors == 6
    assert alerts > 0


def test_encrypted_scenario():
    source = JsonlTrafficSource(ROOT / "data" / "raw" / "scenarios" / "08_encrypted.jsonl")
    flows, vectors, results, alerts = run_pipeline(source)
    assert flows == 1 and vectors == 1
    assert alerts == 1

