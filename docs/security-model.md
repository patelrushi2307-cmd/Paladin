# Security Model

Paladin is designed for a receive-only monitoring enclave.

Capabilities: observe, aggregate, analyze, score, alert, visualize, and store.

Non-capabilities: probe, transmit, resolve DNS externally, initiate handshakes, decrypt TLS/QUIC, extract plaintext, block, or mitigate.

These are architectural constraints, not optional UI settings. Offline replay parses files and emits internal events; it never sends reconstructed packets to a network interface. The detector layer receives FeatureVectors only. The security self-test checks the invariant constants and scans for prohibited active operations.
