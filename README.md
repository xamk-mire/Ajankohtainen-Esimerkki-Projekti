# Exercise Progress Tracker

Full-stack app for logging **training sessions**, viewing personal progress, and (later) AI-assisted feedback from your own history. This repository is a monorepo: FastAPI in `backend/`, React (Vite + TypeScript) in `frontend/`, course tickets in `docs/sprints/`.

**Sprint 1** is Compose (Postgres, API, Vite UI). **Sprint 2** adds the exercise catalog, SQLAdmin, and JWT register/login. Sessions and plans are Sprint 3.

Sprint guide: [docs/sprints/README.md](docs/sprints/README.md) · Sprint 2 demo script: [docs/sprints/tickets/sprint-02-tickets.md](docs/sprints/tickets/sprint-02-tickets.md) (intro → *Suggested demo flow*)

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

Wait until `db` is healthy and `api` / `web` are running. Apply the schema and catalog seed:

```powershell
docker compose exec api alembic upgrade head
docker compose exec api python -m app.db.init_db
```

Generate a real `JWT_SECRET` in `.env` (do not commit that file). Example:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Then recreate `api` so it picks up the secret (`docker compose up -d --force-recreate api`).

Stop (keeps the Postgres volume):

```powershell
docker compose down
```

Never commit `.env`. The committed template is `.env.example`. Compose `web` already sets `VITE_API_BASE_URL` for the browser; copy `frontend/.env.example` → `frontend/.env` only if you run Vite on the host.

## Two logins (do not mix these)

A JWT from the app **will not** open SQLAdmin. The SQLAdmin password **will not** call `/auth/me` or sign you into the UI.

| URL | Purpose | Credentials |
| --- | --- | --- |
| http://localhost:5173/register then http://localhost:5173/login | **App user** — JWT in `localStorage`, header profile from `/auth/me` | Email / password you create in Register. Not the SQLAdmin user. |
| http://localhost:8000/admin | **SQLAdmin** — browse Postgres tables | `SQLADMIN_USERNAME` / `SQLADMIN_PASSWORD` from `.env` (local default `admin` / `admin`). Change these on shared machines. Not a JWT. |
| http://localhost:8000/docs | OpenAPI — try register / login / me | No UI login. For `/auth/me`, Authorize with a Bearer token from `POST /auth/login`. |

## Create the first app user

1. Copy `.env.example` → `.env` at the repo root. Set a long random `JWT_SECRET`. Keep `CORS_ORIGINS=http://localhost:5173` unless you open the UI on another origin.
2. Start Compose, then run `alembic upgrade head` and `python -m app.db.init_db` (commands above).
3. Open http://localhost:5173/register. Fill **display name**, **email**, and **password** (at least 8 characters; a demo value is `demo-pass-1`). Submit. Register does **not** issue a JWT — you are sent to Login.
4. Sign in at http://localhost:5173/login. Home (`/`) should load; the header shows your **display name** (or email).
5. **Log out** clears the token and returns to Login. Opening `/` while logged out redirects to Login.

Duplicate email on register → **409** on the form. Wrong login → **Incorrect email or password**.

## URLs

| Service | Port | Open this |
| --- | --- | --- |
| `web` (Vite UI) | 5173 | http://localhost:5173 |
| `api` health | 8000 | http://localhost:8000/health (process up) |
| `api` DB health | 8000 | http://localhost:8000/health/db (Postgres reachable; 503 if not) |
| `api` OpenAPI | 8000 | http://localhost:8000/docs |
| `api` SQLAdmin | 8000 | http://localhost:8000/admin (env login, **not** JWT) |
| `db` (Postgres) | 5432 | not a web page — used by the API |

The frontend is React + TypeScript (Vite) with **Tailwind CSS** and **shadcn/ui**. Open the UI as **http://localhost:5173** (not `127.0.0.1`) so it matches `CORS_ORIGINS`. The browser calls `http://localhost:8000`, not Compose hostnames `api` or `db`.

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

`s205_initial` creates `users`, `activity_types`, `unit_types`, and `activity_type_unit_types`. `s301_sessions` adds `workout_sessions`, `workout_session_items`, and `workout_session_measurements` (`planned_value` and `actual_value`, both nullable). `plan_id` is added in the plans migration (S3-03), after `workout_plans` exists. There is no `workout_plan_sessions` table and no session-template flag. `s302_goals` adds `goals`: a week or month `target_value` for a `unit_type_id` (optional `activity_type_id`). That is a period target, not `planned_value` on a session.

### Catalog seed

After migrations, load system units, exercise types, and their unit links (idempotent — safe to run twice):

```powershell
docker compose exec api python -m app.db.init_db
```

Sprint 3 uses this catalog. After seed, SQLAdmin should show:

| In `/admin` | What to look for |
| --- | --- |
| Unit types | Four system units: `duration_min`, `distance_km`, `reps`, `weight_kg` |
| Activity types | Exercise-level rows (running, cycling, swimming, hiking, bench_press, curls, face_pull, …) plus `other` |
| Activity↔unit links | Running → duration + distance; a strength exercise (e.g. bench press) → reps + weight with `per_set` |

When you add a new ORM model later, register a `ModelView` in `backend/app/admin.py` in the same change. Keep `password_hash` (and other secrets) out of list, detail, and form columns. SQLAdmin login stays `SQLADMIN_*` from `.env` — a JWT still will not open `/admin`.

## Auth API

`POST /auth/register` creates an app user and returns **public fields only** (`id`, `email`, `display_name`) with **201**. It does **not** issue a JWT — call login next. Duplicate email → **409**. Password and `password_hash` never appear in the response.

Register **password rules** (422 if they fail): at least **8** characters, at most **72** (bcrypt limit), and not a small common list (`password`, `password1`, `12345678`, `123456789`, `qwerty123`, `letmein1`). Login still accepts existing hashes; it does not re-check complexity. A predictable demo password is `demo-pass-1`.

`POST /auth/login` returns `{ "access_token": "<jwt>", "token_type": "bearer" }`. Unknown email and wrong password both return **401** with the same message (`Incorrect email or password`) so accounts cannot be enumerated. Register and login share one email normalizer: addresses are stored and looked up **lowercased**, so `Alex@Example.com` and `alex@example.com` are the same account.

`GET /auth/me` is protected: send `Authorization: Bearer <jwt>`. Missing, invalid, or expired tokens → **401**. Success → public profile (`id`, `email`, `display_name`) only.

The UI stores **only** the JWT in `localStorage` (`access_token`) after login. The shared API client sends `Authorization: Bearer <token>` whenever that key is set. `/` is behind a protected layout; `/login` and `/register` stay public.

Auth smoke test (no UI, SQLite via `get_db` override) from `backend/`:

```powershell
pytest
```

That covers register → login → `GET /auth/me`, and asserts **401** without a token. After rebuilding `api`, `docker compose exec api pytest` works the same.

If you run Uvicorn on the host instead of Compose, from `backend/` (venv with `requirements.txt`, `.env` pointing at `localhost`):

```powershell
alembic upgrade head
python -m app.db.init_db
```

## Configuration

Root `.env` (from `.env.example`). Placeholders only in Git — put real secrets in `.env`.

| Variable | Used for |
| --- | --- |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Compose `db` |
| `DATABASE_URL` | Local Uvicorn (`localhost`). Compose overrides host to `db` |
| `API_HOST`, `API_PORT` | Documented bind; container CMD uses `0.0.0.0:8000` |
| `CORS_ORIGINS` | SPA allowlist (exact origins, comma-separated). Default `http://localhost:5173` — not `*`, not `127.0.0.1`, not Compose host `web`. Allows `GET`/`POST`/`OPTIONS` and `Authorization` / `Content-Type`. JWT uses Bearer headers, so `allow_credentials` is off. |
| `SQLADMIN_USERNAME`, `SQLADMIN_PASSWORD`, `SQLADMIN_SECRET_KEY` | `/admin` only (default `admin`/`admin`). Change on shared machines. Not app-user login. |
| `JWT_SECRET`, `ACCESS_TOKEN_EXPIRE_MINUTES` | App-user JWT signing and expiry (not SQLAdmin). Use a long random `JWT_SECRET` in `.env`. |

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
| JWT does not open `/admin` (or admin password does not open the app) | Two separate logins — see [Two logins](#two-logins-do-not-mix-these) |
| UI does not update on OneDrive | Vite in Compose uses polling; if it is still stuck, restart `web`: `docker compose restart web` |
| API cannot reach Postgres from a container | Do not use `localhost` as the DB host **inside** `api` — Compose sets host `db` |
| `web` fails with `Cannot find package '@tailwindcss/vite'` | The `web_node_modules` volume is stale. Stop Compose, then `docker compose up --build`. The `web` container now runs `npm install` on start. |
| `relation "users" does not exist` (or similar) | Schema is not applied yet. Rebuild `api` if Alembic is missing, then `docker compose exec api alembic upgrade head` |
| Empty unit/activity lists in `/admin` | Run the catalog seed: `docker compose exec api python -m app.db.init_db` |

## Coming next

Sprint 3 adds training sessions, clone, plans, and a calendar on top of this catalog and JWT shell.

## Layout

```text
backend/     FastAPI app (layered api → services → repositories)
frontend/    React + TypeScript (Vite)
docs/sprints/  Tickets and report templates
```
