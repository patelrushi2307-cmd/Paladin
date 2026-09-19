# Passive Ingestion and Replay

Part 2 reads offline input and emits internal normalized `FlowEvent` objects. The replay engine does not transmit packets, open interfaces, initiate connections, or recreate traffic on a network.

## Sources

- `JsonlTrafficSource` reads one JSON object per line, validates it with `FlowEvent`, and skips malformed records while counting them.
- `PcapTrafficSource` uses Scapy `PcapReader` incrementally. It supports IPv4/IPv6 TCP, UDP, and ICMP metadata and skips unsupported packets.
- `FlowAggregator` groups packet-derived records by deterministic 5-tuple, applies idle/max-duration expiry, and emits a finalized flow.

## Replay

`ReplayController` supports real-time timestamp spacing, accelerated spacing, and fixed-rate flow emission. It exposes pause, resume, stop, restart, session ID, progress, and actual measured rate. Historical event timestamps remain in `FlowEvent.timestamp`; processing time is measured separately with monotonic clocks.

## Queue and backpressure

`FlowEventBus` is an in-process bounded `asyncio.Queue`. Producers wait briefly for capacity. If capacity is not available, the event is dropped explicitly, logged as `QUEUE_OVERFLOW`, and counted in metrics. Part 3 subscribes to the manager through `IngestManager.subscribe()`.

## Safe paths

Replay API paths must resolve beneath `DATA_ROOT`, use `.pcap` or `.jsonl`, and respect `REPLAY_MAX_FILE_MB`. The browser receives only the safe relative source list.

## Endpoints

`/api/ingest/status`, `/api/ingest/metrics`, `/api/replay/sources`, `/api/replay/load`, `/api/replay/start`, `/api/replay/pause`, `/api/replay/resume`, `/api/replay/stop`, and `/api/replay/restart`.

## Runtime measurements

Ingest metrics are computed from emitted events and a rolling processing window. The dashboard does not display fabricated traffic values.
