# Threat Model

Paladin is a sensor inside an isolated monitoring enclave. Its primary safety property is that observation cannot become interaction.

## Excluded actions

- **Active probing:** no raw outbound sockets, pings, port scans, DNS lookups, handshakes, or packet crafting.
- **Payload decryption:** TLS and QUIC payloads are never decrypted. Detection uses metadata and traffic shape only.
- **Inline mitigation:** alerts are intelligence outputs. The ingest path has no block, firewall, reset, or control command.
- **Return path:** the service reads from a one-way source and never transmits toward the monitored network.

These controls are represented as constants in `backend/app/system_contract.py` and exposed by the system status/config endpoints. Future code should preserve those invariants and add only passive adapters.
