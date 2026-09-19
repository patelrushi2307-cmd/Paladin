# Encrypted Traffic Detector

`EncryptedTrafficDetector` is metadata-only. It uses observed TLS/QUIC protocol metadata, TLS version, SNI presence, JA3/JA3S/JA4, packet-size statistics, timing, periodicity, and flow volume. It never accesses plaintext, private keys, TLS handshakes, QUIC decryption, or external endpoints. Missing TLS/QUIC metadata returns `not_applicable`; missing fingerprints are permitted. A score means anomalous encrypted-session behavior, not confirmed malware. The evidence explicitly carries `payload_decryption: false`.

Raw categorical fingerprints are not fed into a numeric model in the hot path. Future models must use a known vocabulary, frequency encoding, hashing, or model-side preprocessing. No trained artifact is included.
