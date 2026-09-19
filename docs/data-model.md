# Data Model

Pydantic models under `backend/app/schemas` are the backend source of truth. The frontend mirrors their public fields in `frontend/src/types/contracts.ts` until generated OpenAPI types are introduced.

## FlowEvent

A normalized passive flow: identity, timestamp, endpoints, protocol, packet/byte counts, duration, direction, source adapter, and optional DNS/TLS metadata. Optional metadata means observed metadata only; it never implies payload access.

## FeatureVector

Contains a flow reference, timestamp, values, and an explicit `available` set. A future extractor should only add a feature to `available` when it was actually derivable.

## Alert

Contains alert ID, timestamp, flow ID, extensible threat class, fixed severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), 0-1 confidence score, endpoints, protocol, structured evidence, detector, model version, and observation window. Confidence is not yet a statistically calibrated probability.

## SystemStatus

Reports service and ingest state, receive-only posture, decryption and return-path invariants, active detectors, measured flow rate/throughput, alert count, and last event time. Initial metrics are zero because no source is connected.

## RealtimeEvent

A typed envelope for heartbeat, system status, or alert events sent through `/ws/events`.
