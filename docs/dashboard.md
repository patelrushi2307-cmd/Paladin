# Dashboard

The dashboard uses one WebSocket connection and bounded frontend state. It displays live ingest/feature/detector metrics, replay controls, detector results, final alert events, passive DNS/TLS panels, and empty/disconnected states. `/alerts` provides searchable history and lifecycle actions; `/performance`, `/models`, and `/architecture` provide runtime, model fallback, and security posture views.

Detector results are not final alerts. Final alert rows come from SQLite-backed `/api/alerts` and `ALERT_CREATED`/`ALERT_UPDATED` events. No UI action blocks, isolates, kills, or mitigates traffic.
