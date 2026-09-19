from fastapi.testclient import TestClient
from app.main import app
from app.repositories import AlertRepository
from app.system_contract import ACTIVE_PROBING, INLINE_MITIGATION, ONE_WAY_ONLY, PAYLOAD_DECRYPTION

client = TestClient(app)


def test_security_invariants_are_disabled() -> None:
    assert ONE_WAY_ONLY is True
    assert PAYLOAD_DECRYPTION is False
    assert ACTIVE_PROBING is False
    assert INLINE_MITIGATION is False


def test_status_exposes_receive_only_posture() -> None:
    response = client.get("/api/system/status")
    assert response.status_code == 200
    body = response.json()
    assert body["receive_only"] is True
    assert body["payload_decryption"] is False
    assert body["return_path"] is False


def test_database_initialization(tmp_path) -> None:
    repository = AlertRepository(f"sqlite:///{tmp_path / 'test.db'}")
    repository.initialize()
    assert repository.list_alerts() == []
