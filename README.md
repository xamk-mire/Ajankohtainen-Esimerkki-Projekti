# Exercise Progress Tracker

Full-stack app for logging **training sessions**, viewing personal progress, and (later) AI-assisted feedback from your own history. This repository is a monorepo: FastAPI in `backend/`, React (Vite + TypeScript) in `frontend/`, course tickets in `docs/sprints/`.

**Sprint 1** is the building: Docker Compose starts Postgres, the API, and a placeholder UI. There is no login, exercise catalog, or `/admin` yet—those arrive in Sprint 2.

Sprint guide: [docs/sprints/README.md](docs/sprints/README.md)

## Prerequisites

- [Docker Desktop](https://docs.docker.com/desktop/) (Compose v2: `docker compose`)
- Optional, only if you run services **without** Compose:
  - Python 3.12+ (local Uvicorn)
  - Node.js 22+ and npm (local Vite)

GitHub Actions (`.github/workflows/smoke.yml`) installs backend deps and imports `app.main:app` on every push and pull request.

## Quick start (Compose)

From the repository root in **Windows PowerShell**:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Wait until `db` is healthy and `api` / `web` are running. Then open the URLs below.

Stop (keeps the Postgres volume):

```powershell
docker compose down
```

Never commit `.env`. The committed template is `.env.example`. Compose `web` already sets `VITE_API_BASE_URL` for the browser; copy `frontend/.env.example` → `frontend/.env` only if you run Vite on the host.

## URLs

| Service | Port | Open this |
| --- | --- | --- |
| `web` (Vite UI) | 5173 | http://localhost:5173 |
| `api` health | 8000 | http://localhost:8000/health (process up) |
| `api` DB health | 8000 | http://localhost:8000/health/db (Postgres reachable; 503 if not) |
| `api` OpenAPI | 8000 | http://localhost:8000/docs |
| `db` (Postgres) | 5432 | not a web page — used by the API |

The frontend is React + TypeScript (Vite) with **Tailwind CSS** and **shadcn/ui**. On the home page, API health should show **OK** (the browser calls `http://localhost:8000`, not Compose hostnames `api` or `db`).

## What Compose runs

| Service | Role |
| --- | --- |
| `db` | PostgreSQL 16 (named volume `postgres_data`) |
| `api` | FastAPI / Uvicorn (`backend/Dockerfile`) |
| `web` | Vite **dev server** in Docker (hot reload, not nginx) |

Inside the `api` container, `DATABASE_URL` uses hostname `db`. Your local `.env` keeps `localhost` for Uvicorn on Windows. `web` uses `VITE_API_BASE_URL=http://localhost:8000` so the **browser** can reach the API.

## Configuration (Sprint 1)

Root `.env` (from `.env.example`):

| Variable | Used for |
| --- | --- |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Compose `db` |
| `DATABASE_URL` | Local Uvicorn (`localhost`). Compose overrides host to `db` |
| `API_HOST`, `API_PORT` | Documented bind; container CMD uses `0.0.0.0:8000` |
| `CORS_ORIGINS` | Allowlist for Vite (`http://localhost:5173`) |

Frontend (host Vite only): `VITE_API_BASE_URL=http://localhost:8000` in `frontend/.env`.

## Optional: run without Compose

**API** (from `backend/`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend** (from `frontend/`):

```powershell
Copy-Item .env.example .env
npm install
npm run dev
```

Then open http://localhost:5173. Start the API first so the health indicator can succeed.

## Troubleshooting

| Symptom | What to try |
| --- | --- |
| `docker compose` cannot talk to the engine | Start Docker Desktop and wait until it is ready |
| Forgotten `.env` | `Copy-Item .env.example .env` at the **repo root**, then `docker compose up --build` |
| Port 8000, 5173, or 5432 already in use | Stop the other process, or `docker compose down` and start again |
| API exits while Postgres is still starting | Compose waits for `pg_isready`; give `db` a few seconds, then `docker compose ps` / `docker compose logs db` |
| Home page health is **failed** | Confirm http://localhost:8000/health in the browser; CORS allowlist is `http://localhost:5173` (open that origin, not a random port) |
| UI does not update on OneDrive | Vite in Compose uses polling; if it is still stuck, restart `web`: `docker compose restart web` |
| API cannot reach Postgres from a container | Do not use `localhost` as the DB host **inside** `api` — Compose sets host `db` |
| `web` fails with `Cannot find package '@tailwindcss/vite'` | The `web_node_modules` volume is stale. Stop Compose, then `docker compose up --build`. The `web` container now runs `npm install` on start. |

## Coming next (not Sprint 1)

Sprint 2 adds JWT register/login, the exercise catalog, Alembic, and SQLAdmin at `/admin`. Those are **not** required to demo Sprint 1.

## Layout

```text
backend/     FastAPI app (layered api → services → repositories)
frontend/    React + TypeScript (Vite)
docs/sprints/  Tickets and report templates
```
