# Limitations

- PCAP replay is offline simulation of one-way ingest, not a live diode interface.
- Some sources do not provide DNS, TLS, fingerprints, direction, or packet sequence metadata.
- Encrypted traffic classification is inferential metadata analysis, never payload inspection.
- DGA/DNS tunnel, C2, and other behavioral indicators can produce false positives.
- Prototype thresholds require deployment-specific calibration.
- No trusted public dataset or trained artifact is bundled.
- Confidence is not calibrated probability; calibration is not completed.
- PCAP throughput and formal precision/recall/time-to-detect reports remain N/A until representative labeled PCAP and ground-truth runs are supplied.
- Measured throughput depends on local hardware and workload.
