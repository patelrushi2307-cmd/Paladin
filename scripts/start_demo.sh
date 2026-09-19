#!/usr/bin/env sh
printf '%s\n' 'Terminal 1: cd backend && python -m uvicorn app.main:app --reload --port 8000' 'Terminal 2: cd frontend && npm run dev' 'Open http://localhost:5173 and select raw/scenarios/09_mixed_demo.jsonl in Replay Lab.'
