# Detector Layer

The shared `DetectionEngine` consumes `FeatureVector` objects and emits bounded, typed `DetectorResult` objects. Detector results are intelligence outputs, not final alerts. Part 7 will fuse them into alerts.

Active families: `ddos`, `recon`, `c2`, `exfiltration`, `dga_dns`, and `encrypted_malware`. Each detector declares supported scopes, version, applicability, evidence, reasons, and a score from 0 to 1. A score is not a calibrated probability.

The engine uses direct numeric calculations, bounded result history, per-detector latency measurements, and optional model adapters. No fake model artifacts are included. Model adapters load only an explicitly supplied artifact and otherwise return no model score.

## Matrix

| Detector | Primary scopes | Main features |
|---|---|---|
| DDoS | GLOBAL_WINDOW / DESTINATION_WINDOW | rates, source diversity, concentration, SYN/UDP ratios |
| Recon | SOURCE_WINDOW | host/port fan-out, velocity, SYN behavior |
| C2 | PAIR_WINDOW / SOURCE_WINDOW | IAT, CV, periodicity, repeated destination |
| Exfiltration | FLOW / SOURCE_WINDOW | outbound volume, rate, asymmetry, duration |
| DGA/DNS tunnel | FLOW / SOURCE_WINDOW / GLOBAL_WINDOW | DNS lexical and query behavior |
| Encrypted malware-like | FLOW / SOURCE_WINDOW / PAIR_WINDOW | TLS/QUIC metadata, packet sizes, timing |

All six are passive. They do not access raw packets, open observed endpoints, resolve domains, decrypt TLS/QUIC, or issue mitigation.

Thresholds and weights are prototype engineering values. They require deployment-specific calibration and do not claim universal accuracy.

## APIs

- `GET /api/detectors/status`
- `GET /api/detectors/results/recent`
- `GET /api/detectors/{detector_name}/status`
- WebSocket event `DETECTION_RESULT`
