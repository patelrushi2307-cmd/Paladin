# DDoS Detector

`DDoSDetector` uses passive flow/window features: packet and byte rates, source diversity/entropy, destination concentration, burst rates, and TCP/UDP ratios. Its rule score is a bounded weighted indicator of observed flood-like behavior. Reasons are emitted only when the supporting component crosses its prototype threshold.

A high SYN ratio, UDP ratio, or source diversity is evidence, not proof of a SYN flood, amplification, or spoofing. Model input ordering is explicit in `DDoSModelFeatures.names`; no trained artifact is required.
