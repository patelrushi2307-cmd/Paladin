# Performance Profile

Profile source: `scripts/profile_pipeline.py` using the actual synthetic PCAP and full pipeline.

Measured on the 22-packet fixture:

| Stage | Observation |
|---|---|
| PCAP parser | Lazy Scapy imports dominate the first-run tiny-fixture profile; this is startup cost, not steady-state packet work. |
| Flow aggregation | No material hotspot in the profile. |
| Feature engine | Mean measured feature latency was approximately 0.27 ms in the direct PCAP benchmark. |
| Detector engine | Mean measured detector latency was approximately 0.019 ms. |
| Alert/SQLite | Repeated SQLite repository operations are the largest recurring application-side cost in the profile. |
| WebSocket | Not included in the offline benchmark loop; browser delivery is separately smoke-tested. |

The current implementation favors correctness and per-alert persistence. A production optimization should batch alert writes behind a bounded writer while preserving lifecycle ordering; this was not applied speculatively in the final prototype. The PCAP benchmark measured 88.91 flows/sec on the 22-packet synthetic fixture; this tiny run is dominated by parser startup and is not a sustained throughput claim.
