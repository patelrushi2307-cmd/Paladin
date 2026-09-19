from datetime import datetime, timezone
from app.detectors.c2 import C2BeaconDetector
from app.detectors.exfil import ExfiltrationDetector
from app.schemas.feature import FeatureVector


def vector(values, scope):
    return FeatureVector(feature_id="f", flow_id="flow", timestamp=datetime.now(timezone.utc), scope=scope, source_type="test", values=values, availability={k: v is not None for k, v in values.items()})


def test_periodic_c2_requires_observations_and_scores_regular_behavior():
    values = {"observation_count": 8, "iat_mean": 30, "iat_std": .1, "iat_cv": .003, "periodicity_score": .99, "repeated_destination_ratio": .9, "destination_concentration": .9, "flow_duration": 1, "flows_total": 8, "bytes_total": 1000, "packets_total": 20, "bytes_per_sec": 10}
    result = C2BeaconDetector().detect(vector(values, "SOURCE_WINDOW"), {})[0]
    assert result.score > .8
    assert "strong_periodicity" in result.reasons


def test_c2_insufficient_evidence_is_not_detection():
    result = C2BeaconDetector().detect(vector({"observation_count": 2}, "SOURCE_WINDOW"), {})[0]
    assert result.applicability == "insufficient_evidence"
    assert result.detected is False


def test_exfil_unknown_direction_is_safe():
    result = ExfiltrationDetector().detect(vector({"outbound_bytes": 100000000, "inbound_bytes": 1}, "FLOW"), {})[0]
    assert result.applicability == "insufficient_direction_evidence"
    assert result.score == 0


def test_exfil_outbound_asymmetry():
    values = {"direction_class": "OUTBOUND", "outbound_bytes": 50_000_000, "inbound_bytes": 1_000_000, "outbound_rate": 2_000_000, "outbound_inbound_ratio": 50, "flow_duration": 120, "bytes_total": 51_000_000, "unique_dst_hosts": 1, "current_bytes_vs_baseline": 10}
    result = ExfiltrationDetector().detect(vector(values, "FLOW"), {})[0]
    assert result.score > .7
    assert "strong_outbound_inbound_asymmetry" in result.reasons
