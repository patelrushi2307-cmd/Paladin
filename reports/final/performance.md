# Performance

Environment: local Windows development machine; exact hardware inventory not captured.

Target: 500 flows/sec prototype target.
Measured mixed JSONL pipeline: 220.18 events/sec.
Feature latency: 0.3666 ms average.
Detector latency: 0.0156 ms average.
Drops: not observed in this 36-flow run.
Synthetic PCAP fixture benchmark: 22 packets, 22 flows, 22 FeatureVectors, 132 DetectorResults, 13 alerts, 86.03 packets/sec, 86.03 flows/sec, 0.1448 Mbps, 0.259 ms feature latency, 0.0194 ms detector latency, 0 malformed packets, 0 unsupported packets, 0 detector errors.
Representative real-world PCAP benchmark: N/A; no real capture supplied.
P50/P95/P99: N/A; insufficient sample count for a meaningful final latency distribution.
