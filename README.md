# Exercise Progress Tracker

This repository is a monorepo for the Exercise Progress Tracker course project: `backend/` will hold the FastAPI API, `frontend/` the React (Vite + TypeScript) SPA, and `docs/` the sprint tickets, templates, and course materials. Later tickets in Sprint 1 will add a placeholder UI; this README is only a layout stub until S1-13.

## Docker Compose (`db` + `api`)

Copy `.env.example` → `.env`, then from the repo root:

```bash
docker compose up --build
```

Published ports:

| Service | Host port | URL / notes |
| --- | --- | --- |
| `api` | 8000 | http://localhost:8000/health and http://localhost:8000/docs |
| `db` | 5432 | PostgreSQL (`POSTGRES_*` from `.env`) |

`DATABASE_URL` in `.env` stays on `localhost` for local Uvicorn. Compose overrides it for the `api` container so the host is the `db` service. The API waits until Postgres is healthy (`pg_isready`) before starting.

## Run the API locally (without Compose)

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

## Run the frontend locally

From `frontend/`:

```powershell
npm install
npm run dev
```

Open the URL Vite prints (usually http://localhost:5173).

## Configuration

Copy `.env.example` → `.env` at the repo root. Git ignores `.env`; commit only the example.

| Variable | API reads it today | When it is used |
| --- | --- | --- |
| `API_HOST`, `API_PORT` | Yes (settings) | Local Uvicorn still uses the CLI flags; Compose/Dockerfile will match these |
| `CORS_ORIGINS` | Yes (settings) | CORS middleware in S1-11 (`http://localhost:5173`) |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Yes (settings) | Compose `db` service in S1-07 |
| `DATABASE_URL` | Yes (settings) | Local Uvicorn: `localhost`. Compose `api` service: hostname `db` (override in `docker-compose.yml`) |
