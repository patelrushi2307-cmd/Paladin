from datetime import datetime, timezone
from app.detectors.ddos import DDoSDetector
from app.detectors.recon import ReconDetector
from app.schemas.feature import FeatureVector


def vector(values, scope="GLOBAL_WINDOW"):
    return FeatureVector(feature_id="f", flow_id="flow", timestamp=datetime.now(timezone.utc), scope=scope, source_type="test", values=values, availability={key: value is not None for key, value in values.items()})


def test_ddos_high_rate_is_bounded_and_evidenced():
    values = {"packets_per_sec": 5000, "bytes_per_sec": 5_000_000, "flows_per_sec": 1000, "unique_src_count": 100, "source_ip_entropy": 5, "destination_concentration": .95, "syn_ratio": .95, "ack_ratio": .05, "udp_ratio": 0, "burst_packets_per_sec": 5000, "burst_bytes_per_sec": 5_000_000}
    result = DDoSDetector().detect(vector(values), {})[0]
    assert result.score > .5
    assert result.score <= 1
    assert "high_destination_concentration" in result.reasons


def test_recon_high_fanout_is_detected():
    values = {"fanout_hosts": 100, "fanout_ports": 3, "scan_velocity": 30, "unique_dst_hosts": 100, "unique_dst_ports": 3, "syn_ratio": .8, "destination_ip_entropy": 5, "packets_per_sec": 100}
    result = ReconDetector().detect(vector(values, "SOURCE_WINDOW"), {})[0]
    assert result.score > .5
    assert "high_host_fanout" in result.reasons


def test_scope_is_respected():
    assert ReconDetector().detect(vector({}, "GLOBAL_WINDOW"), {}) == []
