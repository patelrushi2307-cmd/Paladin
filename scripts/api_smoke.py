"""Offline API and WebSocket contract smoke test."""
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))
from app.main import app
client = TestClient(app)
for endpoint in ("/api/health", "/api/system/status", "/api/ingest/status", "/api/features/status", "/api/detectors/status", "/api/alerts", "/api/alerts/summary", "/api/models/status", "/api/docs"):
    response = client.get(endpoint); assert response.status_code == 200, (endpoint, response.status_code)
with client.websocket_connect("/ws/events") as websocket:
    assert websocket.receive_json()["event_type"] == "heartbeat"
print("API SMOKE: PASS")
