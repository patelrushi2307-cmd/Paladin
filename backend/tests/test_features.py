from datetime import datetime, timedelta, timezone
import json

from app.features.direction import classify_direction, is_internal_ip, parse_networks
from app.features.engine import FeatureEngine
from app.features.math_utils import coefficient_of_variation, periodicity_score, shannon_entropy
from app.features.dns import dns_features, normalize_query
from app.schemas.flow import FlowEvent


def make_event(index: int, timestamp: datetime, **overrides) -> FlowEvent:
    data = {"event_id": f"flow-{index}", "timestamp": timestamp, "src_ip": "10.0.0.5", "dst_ip": "8.8.8.8", "src_port": 50000 + index, "dst_port": 443, "protocol": "TCP", "packets": 10, "bytes": 1000, "duration": 0.1, "direction": "outbound", "source_type": "test", "tcp_flags": "SA", "tls_version": "TLSv1.3", "tls_sni": "example.org"}
    data.update(overrides)
    return FlowEvent.model_validate(data)


def test_entropy_math() -> None:
    assert shannon_entropy([]) is None
    assert shannon_entropy(["a"]) == 0
    assert shannon_entropy(["a", "a", "a"]) == 0
    assert abs(shannon_entropy(["a", "b"]) - 1) < 1e-9
    assert shannon_entropy(["a", "a", "b"]) < 1


def test_temporal_periodicity() -> None:
    intervals = [0.5, 0.5, 0.5]
    assert coefficient_of_variation(intervals) == 0
    assert periodicity_score(intervals) == 1
    assert periodicity_score([0.1, 1.5, 0.2, 3.0]) < 1


def test_dns_is_passive_and_normalized() -> None:
    assert normalize_query("EXAMPLE.COM.") == ("example.com", ["example", "com"])
    assert normalize_query("8.8.8.8")[0] is None
    values, available = dns_features("x8j29dk29q8s1m7.example.org", "TXT")
    assert values["dns_query_length"] > 0
    assert values["txt_record"] is True
    assert available["dns_query_entropy"] is True
    assert values["ngram_score"] is None


def test_direction_model() -> None:
    networks = parse_networks("10.0.0.0/8")
    assert is_internal_ip("10.0.0.5", networks) is True
    assert classify_direction("10.0.0.5", "8.8.8.8", networks) == "OUTBOUND"
    assert classify_direction("8.8.8.8", "10.0.0.5", networks) == "INBOUND"
    assert classify_direction("10.0.0.5", "10.0.0.6", networks) == "INTERNAL_INTERNAL"
    assert classify_direction("bad", "10.0.0.6", networks) == "UNKNOWN"


def test_feature_engine_is_incremental_serializable_and_deterministic() -> None:
    start = datetime(2026, 9, 19, tzinfo=timezone.utc)
    events = [make_event(index, start + timedelta(seconds=index * 0.5), dst_ip=f"8.8.8.{index + 1}") for index in range(4)]
    engine = FeatureEngine()
    vectors = [engine.process(event) for event in events]
    payload = json.dumps(vectors[-1].model_dump(mode="json"), allow_nan=False)
    assert "NaN" not in payload and "Infinity" not in payload
    assert vectors[-1].values["iat_mean"] == 0.5
    assert vectors[-1].values["periodicity_score"] == 1
    assert vectors[-1].values["source_ip_entropy"] == 0
    assert vectors[-1].availability["dns_query_entropy"] is False
    assert vectors[-1].values["tls_metadata_available"] is True
    assert engine.status()["recent_feature_vectors"] == 4


def test_feature_state_is_bounded() -> None:
    engine = FeatureEngine()
    engine.state.max_items = 3
    start = datetime(2026, 9, 19, tzinfo=timezone.utc)
    for index in range(20):
        engine.process(make_event(index, start + timedelta(seconds=index), src_ip=f"10.0.0.{index + 1}"))
    assert len(engine.state.events) <= 60
    assert all(len(state.timestamps) <= 3 for state in engine.state.source_states.values())
