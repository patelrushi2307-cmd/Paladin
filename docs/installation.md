# Installation

## Local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
cd frontend
npm install
```

Start backend:

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Start frontend in a second terminal:

```powershell
cd frontend
npm run dev
```

Open `http://localhost:5173`. Run `python scripts/final_validation.py` from the repository root.

## Docker

```powershell
docker compose up --build
```

Docker runtime validation requires Docker Desktop or another Docker installation. The repository can still be fully validated locally without Docker.
