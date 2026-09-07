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

Wait until `db` is healthy and `api` / `web` are running. Apply the schema and catalog seed, then open the URLs below.

```powershell
docker compose exec api alembic upgrade head
docker compose exec api python -m app.db.init_db
```

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
| `api` SQLAdmin | 8000 | http://localhost:8000/admin (env login, not JWT) |
| `db` (Postgres) | 5432 | not a web page — used by the API |

The frontend is React + TypeScript (Vite) with **Tailwind CSS** and **shadcn/ui**. On the home page, API health should show **OK** (the browser calls `http://localhost:8000`, not Compose hostnames `api` or `db`).

## What Compose runs

| Service | Role |
| --- | --- |
| `db` | PostgreSQL 16 (named volume `postgres_data`) |
| `api` | FastAPI / Uvicorn (`backend/Dockerfile`) |
| `web` | Vite **dev server** in Docker (hot reload, not nginx) |

Inside the `api` container, `DATABASE_URL` uses hostname `db`. Your local `.env` keeps `localhost` for Uvicorn on Windows. `web` uses `VITE_API_BASE_URL=http://localhost:8000` so the **browser** can reach the API.

## Database migrations (Alembic)

Schema changes live in `backend/alembic/versions/` and use the same `DATABASE_URL` as the API. After Compose is up (or after you recreate the Postgres volume), apply migrations **inside the API container**:

```powershell
docker compose exec api alembic upgrade head
```

That creates `users`, `activity_types`, `unit_types`, and `activity_type_unit_types`.

### Catalog seed

After migrations, load system units, exercise types, and their unit links (idempotent — safe to run twice):

```powershell
docker compose exec api python -m app.db.init_db
```

This inserts four unit types (`duration_min`, `distance_km`, `reps`, `weight_kg`), cardio and strength exercises (plus `other`), and the activity↔unit links (Running → duration + distance; Bench press → reps + weight per set).

## SQLAdmin (`/admin`)

Browse Postgres in the browser at http://localhost:8000/admin. This login is **not** the later JWT app-user login.

Default local credentials (from `.env.example`): `admin` / `admin`. Change `SQLADMIN_USERNAME`, `SQLADMIN_PASSWORD`, and `SQLADMIN_SECRET_KEY` on shared machines. After seed you should see unit types, exercise activity types, and activity↔unit links (including Running’s duration + distance and a strength exercise’s `per_set` flags).

## Auth API

`POST /auth/register` creates an app user and returns **public fields only** (`id`, `email`, `display_name`) with **201**. It does **not** issue a JWT — call login next. Duplicate email → **409**. Password and `password_hash` never appear in the response.

`POST /auth/login` returns `{ "access_token": "<jwt>", "token_type": "bearer" }`. Unknown email and wrong password both return **401** with the same message (`Incorrect email or password`) so accounts cannot be enumerated.

`GET /auth/me` is protected: send `Authorization: Bearer <jwt>`. Missing, invalid, or expired tokens → **401**. Success → public profile (`id`, `email`, `display_name`) only. In http://localhost:8000/docs, log in, copy the token, click **Authorize**, then call `/auth/me`.

The UI register form is http://localhost:5173/register. On success it **navigates to `/login`** (no auto-login — register does not return a JWT). Duplicate email and validation errors are shown on the form.

The UI login form is http://localhost:5173/login. On success it stores **only** the JWT in `localStorage` (`access_token`) and navigates home. The shared API client sends `Authorization: Bearer <token>` whenever that key is set. Wrong email or password shows **Incorrect email or password**.

`/` is behind a protected layout: missing or invalid JWT (including `GET /auth/me` **401**) clears the token and redirects to `/login`. `/login` and `/register` stay public so they do not loop. The header shows **display name** (or email) from `/auth/me`. **Log out** removes the JWT from `localStorage`, drops in-memory user state, and returns to login.

If you run Uvicorn on the host instead of Compose, from `backend/` (venv with `requirements.txt`, `.env` pointing at `localhost`):

```powershell
alembic upgrade head
python -m app.db.init_db
```

## Configuration (Sprint 1)

Root `.env` (from `.env.example`):

| Variable | Used for |
| --- | --- |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Compose `db` |
| `DATABASE_URL` | Local Uvicorn (`localhost`). Compose overrides host to `db` |
| `API_HOST`, `API_PORT` | Documented bind; container CMD uses `0.0.0.0:8000` |
| `CORS_ORIGINS` | SPA allowlist (exact origins, comma-separated). Default `http://localhost:5173` — not `*`, not `127.0.0.1`, not Compose host `web`. Allows `GET`/`POST`/`OPTIONS` and `Authorization` / `Content-Type`. JWT uses Bearer headers, so `allow_credentials` is off. |
| `SQLADMIN_USERNAME`, `SQLADMIN_PASSWORD`, `SQLADMIN_SECRET_KEY` | `/admin` login (default `admin`/`admin`; change on shared machines) |
| `JWT_SECRET`, `ACCESS_TOKEN_EXPIRE_MINUTES` | App-user JWT signing and expiry (not SQLAdmin). Use a long random `JWT_SECRET` in `.env` |

Frontend (host Vite only): `VITE_API_BASE_URL=http://localhost:8000` in `frontend/.env`.

## Optional: run without Compose

**API** (from `backend/`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m app.db.init_db
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
| Home page health is **failed** | Confirm http://localhost:8000/health in the browser; CORS allowlist is `http://localhost:5173` (open that origin, not `127.0.0.1` or a random port) |
| Browser `fetch` to the API fails with a CORS / preflight error | Confirm the page origin matches `CORS_ORIGINS` exactly, rebuild `api` after CORS changes, and check DevTools → Network for a failed `OPTIONS` request |
| UI does not update on OneDrive | Vite in Compose uses polling; if it is still stuck, restart `web`: `docker compose restart web` |
| API cannot reach Postgres from a container | Do not use `localhost` as the DB host **inside** `api` — Compose sets host `db` |
| `web` fails with `Cannot find package '@tailwindcss/vite'` | The `web_node_modules` volume is stale. Stop Compose, then `docker compose up --build`. The `web` container now runs `npm install` on start. |
| `relation "users" does not exist` (or similar) | Schema is not applied yet. Rebuild `api` if Alembic is missing, then `docker compose exec api alembic upgrade head` |

## Coming next (not Sprint 1)

Sprint 2 continues with JWT register/login. Those are **not** required to demo the Sprint 1 shell.

## Layout

```text
backend/     FastAPI app (layered api → services → repositories)
frontend/    React + TypeScript (Vite)
docs/sprints/  Tickets and report templates
```
