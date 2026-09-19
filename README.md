# Paladin

**Observe. Detect. Explain. Never Transmit.**

Paladin is an AI/ML-ready passive cyber-threat detection platform for a monitoring enclave receiving unidirectional IP traffic. It observes normalized flow and protocol metadata, derives features, and eventually emits bounded-latency intelligence alerts. It is not an inline firewall.

## One-way architecture

```text
ONE-WAY TRAFFIC -> PASSIVE INGEST -> STREAMING FLOW ENGINE -> FEATURES
                                                     |        |        |
                                                   DDoS      C2     DNS/DGA
                                                     |        |        |
                                      RECON / EXFIL / TLS-METADATA DETECTORS
                                                               |
                                                        SCORE FUSION
                                                               |
                                                        ALERT ENGINE
                                                               |
                                                        API / WEBSOCKET
                                                               |
                                                          DASHBOARD
```

The receive-only posture is enforced in `backend/app/system_contract.py`: no return path, active probing, payload decryption, packet crafting, or inline mitigation exists in this part.

## Stack

Python 3.11+, FastAPI, Pydantic, Uvicorn, SQLite, Scapy extension point, React, TypeScript, Vite, Recharts-ready frontend, pytest, Docker Compose.

## Repository

- `backend/app/schemas`: source-of-truth Pydantic contracts.
- `backend/app/ingest`, `features`, `detectors`, `scoring`, `alerts`: extension boundaries for future parts.
- `frontend/src/types`: TypeScript representations of backend contracts.
- `data/raw`: benign seed data only; no attack claims.
- `docs`: architecture, data model, threat model, and implementation plan.

## Run locally

Backend (PowerShell):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Frontend in another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The dashboard intentionally shows zero traffic and zero alerts until a real source is connected.

Run tests with `cd backend; python -m pytest -q` and build the UI with `cd frontend; npm run build`.

## Docker

```powershell
docker compose up --build
```

Then open `http://localhost:5173`. SQLite is persisted through the `data` volume.

## API

- `GET /api/health`
- `GET /api/system/status`
- `GET /api/system/config-summary`
- `GET /api/alerts`
- `GET /api/docs`
- `WS /ws/events`

## Parts 2-9 capability

Part 1 provides the contracts and receive-only foundation. Part 2 adds offline PCAP/JSONL ingestion, deterministic flow aggregation, bounded replay, safe source selection, runtime metrics, and replay controls. Part 3 adds bounded event-time state, windows, feature extraction, availability metadata, feature registry, model input utilities, feature APIs, WebSocket feature metrics, and a Feature Inspector. Replay parses observations internally and never sends packets to a network interface.

Parts 4-6 add one shared DetectionEngine with six passive detector families: DDoS, Recon, C2 beaconing, data exfiltration, DGA/DNS tunnelling, and encrypted TLS/QUIC malware-like behavior. Detector results are structured intelligence signals, not final alerts or calibrated probabilities. TLS/QUIC detection uses metadata and traffic shape only; payload decryption remains off.

Part 7 adds transparent score fusion, prototype confidence/severity, normalized evidence, deduplication, correlation, SQLite alert persistence, alert lifecycle APIs, and `ALERT_CREATED`/`ALERT_UPDATED` WebSocket events. Part 8 adds alert investigation, performance, model fallback, and architecture views. Part 9 adds local dataset adapters, manifests, quality/leakage reports, grouped training, model metadata, and measured benchmark/report commands. No external dataset or trained artifact is required at runtime.

Load a `.pcap` or `.jsonl` file beneath `data/`, select it in the dashboard Replay Lab, and choose real-time, accelerated, or fixed-rate mode. The repository includes a clearly labelled synthetic PCAP fixture at `data/raw/synthetic_fixture.pcap`; it is generated offline and never transmitted. JSONL records must conform to `FlowEvent`. Configuration is in `.env.example`, including `DATA_ROOT`, queue size, flow expiry, replay limits, feature windows, state TTL, and internal CIDRs.

Feature endpoints are `GET /api/features/status`, `GET /api/features/recent`, `GET /api/features/{feature_id}`, and `GET /api/features/registry`. Detector endpoints are `GET /api/detectors/status`, `GET /api/detectors/results/recent`, and `GET /api/detectors/{detector_name}/status`. A local seed check is `python scripts/seed_demo_data.py`; benchmarks are `python scripts/benchmark_ingest.py` and `python scripts/benchmark_detectors.py`.

The prototype does not claim attack detection, live source throughput, calibrated confidence, or payload visibility. Features are telemetry, not alerts.

## Future parts

Final validation is available through `python scripts/final_validation.py` using the workspace `.venv` when present. Docker status is reported separately and is not marked PASS when Docker is unavailable. Final reports are under `reports/final/`.

See `docs/development-plan.md` for the exact extension order.
