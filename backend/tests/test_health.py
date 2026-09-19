from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_websocket_accepts_connection() -> None:
    with client.websocket_connect("/ws/events") as websocket:
        assert websocket.receive_json()["event_type"] == "heartbeat"
