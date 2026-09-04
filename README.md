# Exercise Progress Tracker

This repository is a monorepo for the Exercise Progress Tracker course project: `backend/` will hold the FastAPI API, `frontend/` the React (Vite + TypeScript) SPA, and `docs/` the sprint tickets, templates, and course materials. This README is a layout stub until S1-13.

## Docker Compose (`db` + `api` + `web`)

The `web` service runs the **Vite dev server** in Docker (hot reload; not a production nginx build). Copy `.env.example` → `.env`, then from the repo root:

```bash
docker compose up --build
```

Published ports:

| Service | Host port | URL / notes |
| --- | --- | --- |
| `web` | 5173 | http://localhost:5173 |
| `api` | 8000 | http://localhost:8000/health and http://localhost:8000/docs |
| `db` | 5432 | PostgreSQL (`POSTGRES_*` from `.env`) |

`VITE_API_BASE_URL` for `web` is `http://localhost:8000` so the **browser** can reach the API. `DATABASE_URL` in `.env` stays on `localhost` for local Uvicorn. Compose overrides it for the `api` container so the host is the `db` service. The API waits until Postgres is healthy (`pg_isready`) before starting.

On OneDrive-synced folders, Docker file watching can be flaky; the Vite service uses polling.

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

Open the URL Vite prints (usually http://localhost:5173). Copy `frontend/.env.example` → `frontend/.env` so `VITE_API_BASE_URL` is `http://localhost:8000` (a browser URL, not a Compose hostname). The home page shows API health OK / failed.

## Configuration

Copy `.env.example` → `.env` at the repo root. Git ignores `.env`; commit only the example.

| Variable | API reads it today | When it is used |
| --- | --- | --- |
| `API_HOST`, `API_PORT` | Yes (settings) | Local Uvicorn still uses the CLI flags; Compose/Dockerfile will match these |
| `CORS_ORIGINS` | Yes (settings) | CORS allowlist for Vite (`http://localhost:5173`) |
| `VITE_API_BASE_URL` | Frontend only | Browser calls the API at `http://localhost:8000` |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Yes (settings) | Compose `db` service in S1-07 |
| `DATABASE_URL` | Yes (settings) | Local Uvicorn: `localhost`. Compose `api` service: hostname `db` (override in `docker-compose.yml`) |
