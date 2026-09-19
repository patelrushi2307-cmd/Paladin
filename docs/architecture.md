# Architecture

Paladin has one permitted data direction: a passive source enters the monitoring enclave. Application services never send traffic toward production and never require a return path.

## Boundaries

1. `TrafficSource` emits normalized `FlowEvent` objects. Adapters may use offline Scapy PCAP replay or JSONL now; Zeek, NetFlow, IPFIX, and sFlow can be added without changing downstream code.
2. A bounded event bus and `IngestManager` preserve incremental flow delivery. PCAP replay parses files only; it never transmits packets.
3. `StreamingStateManager` maintains TTL-managed flow, source, destination, pair, and event-time window state. `FeatureEngine` converts each event into a `FeatureVector` incrementally.
4. `FeatureExtractor` converts a flow and stream context into a `FeatureVector`. Missing metadata remains unavailable rather than silently becoming zero.
3. `ThreatDetector` implementations inspect features and return structured detector results.
4. `ThreatScorer` reserves score fusion for later parts. Confidence is an engineering score in the range 0-1, not a calibrated probability.
5. `AlertSink` publishes normalized `Alert` objects to storage and realtime consumers.
6. FastAPI provides HTTP status contracts and a WebSocket event envelope. React is a consumer, not a second source of truth.

The current shared detection layer registers DDoS, Recon, C2 beaconing, data exfiltration, DGA/DNS tunnelling, and encrypted TLS/QUIC metadata detectors. Each consumes only `FeatureVector`, declares applicable scopes, and emits `DetectorResult`; Part 7 remains responsible for fusion into alerts.

TLS and QUIC remain encrypted. Only passively observed metadata such as SNI, version, ALPN, fingerprints, packet sizes, and timings may be used where present. No payload decryption is supported.

## Streaming posture

The interfaces are incremental and context-aware. Event time is preserved from the source while processing time is measured with monotonic clocks. State, queues, and recent vectors are bounded and TTL-managed. Kafka, Flink, and Kubernetes are intentionally outside this prototype.

```text
One-way source -> passive ingest -> flow aggregation -> bounded queue
	-> streaming state -> event-time windows -> FeatureVector -> future detectors
```

Feature extraction is pure observation and never performs active DNS, endpoint checks, payload decryption, or network I/O.
