from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from app.schemas.alert import Alert
from app.schemas.flow import FlowEvent


def test_flow_event_validation() -> None:
    event = FlowEvent(
        event_id="flow-1", timestamp=datetime.now(timezone.utc), src_ip="10.0.0.1",
        dst_ip="10.0.0.2", protocol="TCP", packets=2, bytes=100, duration=0.2,
        source_type="test",
    )
    assert event.source_type == "test"
    assert event.dns_query is None


def test_alert_validation() -> None:
    alert = Alert(
        alert_id="alert-1", timestamp=datetime.now(timezone.utc), flow_id="flow-1",
        threat_class="RECON", severity="LOW", confidence_score=0.5,
        source_ip="10.0.0.1", destination_ip="10.0.0.2", protocol="TCP",
        evidence={"fanout_ports": 3}, detector="test", model_version="none",
        observation_window_ms=5000,
    )
    assert alert.confidence_score == 0.5


@pytest.mark.parametrize("field,value", [("confidence_score", -0.1), ("confidence_score", 1.1)])
def test_confidence_is_bounded(field: str, value: float) -> None:
    with pytest.raises(ValidationError):
        Alert(
            alert_id="alert-1", timestamp=datetime.now(timezone.utc), flow_id="flow-1",
            threat_class="RECON", severity="LOW", confidence_score=value,
            source_ip="10.0.0.1", destination_ip="10.0.0.2", protocol="TCP",
            evidence={}, detector="test", model_version="none", observation_window_ms=1,
        )


def test_invalid_severity_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Alert(
            alert_id="alert-1", timestamp=datetime.now(timezone.utc), flow_id="flow-1",
            threat_class="RECON", severity="UNKNOWN", confidence_score=0.5,
            source_ip="10.0.0.1", destination_ip="10.0.0.2", protocol="TCP",
            evidence={}, detector="test", model_version="none", observation_window_ms=1,
        )
