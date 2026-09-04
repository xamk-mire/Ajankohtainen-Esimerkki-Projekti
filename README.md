# Exercise Progress Tracker

This repository is a monorepo for the Exercise Progress Tracker course project: `backend/` will hold the FastAPI API, `frontend/` the React (Vite + TypeScript) SPA, and `docs/` the sprint tickets, templates, and course materials. Later tickets in Sprint 1 will add Docker Compose and a placeholder UI; this README is only a layout stub until S1-13.

## Run the API

From `backend/`:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs for the interactive OpenAPI UI, or http://localhost:8000/health for the liveness check.

## Configuration

Copy `.env.example` → `.env` at the repo root. Git ignores `.env`; commit only the example.

| Variable | API reads it today | When it is used |
| --- | --- | --- |
| `API_HOST`, `API_PORT` | Yes (settings) | Local Uvicorn still uses the CLI flags; Compose/Dockerfile will match these |
| `CORS_ORIGINS` | Yes (settings) | CORS middleware in S1-11 (`http://localhost:5173`) |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Yes (settings) | Compose `db` service in S1-07 |
| `DATABASE_URL` | Yes (settings) | API → Postgres in S1-08. Use `localhost` on your machine; inside the API container the host is `db` |
