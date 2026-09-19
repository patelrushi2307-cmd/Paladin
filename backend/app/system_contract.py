"""Non-negotiable observation-only security posture for the monitoring enclave."""

# Traffic is consumed from a one-way source; the application never transmits to it.
ONE_WAY_ONLY = True
# Encrypted sessions are analyzed through metadata and never decrypted.
PAYLOAD_DECRYPTION = False
# The platform cannot probe, scan, resolve, or initiate connections.
ACTIVE_PROBING = False
# Detection never issues blocking or mitigation commands on the ingest path.
INLINE_MITIGATION = False
