"""Receive-only realtime event channel."""

import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..ingest.runtime import runtime
from ..features.engine import feature_engine
from ..detectors.engine import detection_engine
from ..dependencies import get_alert_service
from ..schemas.realtime import RealtimeEnvelope

router = APIRouter(tags=["realtime"])


@router.websocket("/ws/events")
async def events(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        event = RealtimeEnvelope(
            event_type="heartbeat",
            timestamp=datetime.now(timezone.utc),
            data={"service": "paladin-backend", "status": "ready"},
        )
        await websocket.send_json(event.model_dump(mode="json"))
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
            except asyncio.TimeoutError:
                await websocket.send_json(RealtimeEnvelope(event_type="INGEST_METRICS", timestamp=datetime.now(timezone.utc), data=runtime.status().metrics.model_dump(mode="json")).model_dump(mode="json"))
                await websocket.send_json(RealtimeEnvelope(event_type="REPLAY_STATUS", timestamp=datetime.now(timezone.utc), data=runtime.controller.status().model_dump(mode="json")).model_dump(mode="json"))
                await websocket.send_json(RealtimeEnvelope(event_type="FEATURE_METRICS", timestamp=datetime.now(timezone.utc), data=feature_engine.status()).model_dump(mode="json"))
                recent_result = detection_engine.recent()[0] if detection_engine.recent() else None
                if recent_result:
                    await websocket.send_json(RealtimeEnvelope(event_type="DETECTION_RESULT", timestamp=datetime.now(timezone.utc), data=recent_result.model_dump(mode="json")).model_dump(mode="json"))
                alert_event = get_alert_service().latest_event()
                if alert_event:
                    event_name, alert = alert_event
                    await websocket.send_json(RealtimeEnvelope(event_type=event_name, timestamp=datetime.now(timezone.utc), data=alert.model_dump(mode="json")).model_dump(mode="json"))
    except WebSocketDisconnect:
        return
