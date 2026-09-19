# API Validation

Validated by `scripts/api_smoke.py`:

- `/api/health`: 200
- `/api/system/status`: 200
- `/api/ingest/status`: 200
- `/api/features/status`: 200
- `/api/detectors/status`: 200
- `/api/alerts`: 200
- `/api/alerts/summary`: 200
- `/api/models/status`: 200
- `/api/docs`: 200
- `/ws/events`: heartbeat received

Pagination/filter and alert lifecycle APIs are covered by typed routes and alert repository tests. Docker runtime API validation remains unavailable when Docker is not installed.
