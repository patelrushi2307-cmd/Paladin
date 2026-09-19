# Final Demo Runbook

1. Start backend: `cd backend; python -m uvicorn app.main:app --reload --port 8000`.
2. Start frontend: `cd frontend; npm run dev`.
3. Open `http://localhost:5173` and point out RECEIVE ONLY, RETURN PATH NONE, PAYLOAD DECRYPTION OFF, and the detector panel.
4. In Replay Lab select `raw/scenarios/09_mixed_demo.jsonl` and start replay.
5. Show live FlowEvents, FeatureVectors, detector results, and persisted alerts.
6. Open `/alerts` to inspect evidence and lifecycle status.
7. Open `/performance` for measured runtime values and `/architecture` for the one-way design.
8. Explain that the fixtures are controlled offline observations and that confidence is not calibrated probability.

No internet, DNS, external model, or packet transmission is required.
