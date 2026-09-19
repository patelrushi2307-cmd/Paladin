# C2 Beaconing Detector

`C2BeaconDetector` requires a configurable minimum observation count and uses event-time IAT consistency, periodicity, repeated destination ratio, destination concentration, and persistence. Low-volume periodic traffic can score strongly; volume is contextual rather than primary. A score means beacon-like behavior, not confirmed malware. Missing or insufficient observations return `insufficient_evidence`.
