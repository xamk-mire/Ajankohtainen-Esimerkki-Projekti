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

`s205_initial` creates `users`, `activity_types`, `unit_types`, and `activity_type_unit_types`. `s301_sessions` adds `workout_sessions`, `workout_session_items`, and `workout_session_measurements` (`planned_value` and `actual_value`, both nullable). `s303_plans` adds `workout_plans` and nullable `workout_sessions.plan_id` (ON DELETE SET NULL). One session belongs to at most one plan. There is no `workout_plan_sessions` table and no session-template flag. `s302_goals` adds `goals`: a week or month `target_value` for a `unit_type_id` (optional `activity_type_id`). That is a period target, not `planned_value` on a session.

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

That covers register → login → `GET /auth/me`, and asserts **401** without a token. `tests/test_sessions.py` covers owner-scoped `/sessions` create, list, update, and delete, including nested items. After rebuilding `api`, `docker compose exec api pytest` works the same.

## Sessions API

`/sessions` requires a Bearer token. List, create, read, patch, and delete apply only to the current user. Another user's session id returns **404** `Session not found` (the same response as a missing id). Optional `plan_id` must be a plan you own; otherwise **404** `Plan not found`.

`GET /sessions` filters are combined with the current user: `from`, `to` (inclusive bounds on `session_at`), `status`, `activity_type_id`, `unscheduled` (`true` = no `session_at`, `false` = dated), and `plan_id`. `from` later than `to` is **400**. A `plan_id` you do not own returns an empty list, not that user's sessions.

Create and patch accept nested `items` and `measurements`. Each measurement needs `planned_value`, `actual_value`, or both; both empty is **422**. `unit_type_id` must be linked to that exercise in `activity_type_unit_types`, or the write is **422**. If that link is `per_set`, `set_index` is required. Omitting `items` on patch leaves existing exercises in place. Sending `items` replaces them.

`POST /sessions/{id}/clone` deep-copies your session into a new one (`201`). Planned values and exercise notes are kept; `actual_value` is cleared; status is `planned`; `source_session_id` points at the source. Optional body fields are `name`, `session_at`, and `plan_id`. If `plan_id` or `session_at` is omitted, the clone does not inherit them. Editing the source later does not change the clone. Another user's session id is **404**.

CORS allows `GET`, `POST`, `PATCH`, `DELETE`, and `OPTIONS`.

## Plans API

`/plans` requires a Bearer token and is limited to the current user. Another user's plan id is **404** `Plan not found`. `start_date` and `length_weeks` are metadata only.

`GET /plans/{id}` lists member sessions ordered by `session_at` ascending, with unscheduled sessions (`session_at` null) last. Attach with `POST /plans/{id}/sessions/{session_id}` and detach with `DELETE` on that path. Both set or clear `workout_sessions.plan_id`. There is no junction table. Attaching another user's session is **404** `Session not found`. A session can belong to only one plan, so attaching it moves it off any previous plan.

## Activity types API

`GET /activity-types` requires a Bearer token. It returns system exercises (`user_id` null) and the current user's custom types. Another user's custom type is omitted. Each row includes `unit_links` ordered by `sort_order`, with the linked unit's `slug`, `name`, and `unit_label`, plus `is_required` and `per_set`. There is no `unit_hint`.

`POST /activity-types` creates a custom type owned by the caller (`is_system` false). Body: `name`, optional `slug` (otherwise derived from the name), and at least one `unit_links` entry (`unit_type_id`, optional `sort_order`, `is_required`, `per_set`). An unknown unit or a repeated unit is **422**. A slug you already use is **409**.

## Goals API

`/goals` requires a Bearer token and is limited to the current user. Another user's goal id is **404** `Goal not found`. A goal is a week or month `target_value` for a `unit_type_id`, with an optional `activity_type_id`. It is not `planned_value` on a session.

`unit_type_id` must exist, or the write is **422**. `activity_type_id`, when set, must be a system exercise or one of your custom types. `GET /goals?active=true` or `active=false` filters that flag; omit it to list every goal you own. Deactivate with `PATCH` `{ "active": false }`. `DELETE` returns **204**.

## Period goals

`/goals` is behind the same login gate. It lists this user's period goals from `GET /goals`. **Create period goal** sends `unit_type_id`, a target greater than 0, and `week` or `month`. An exercise is optional. These are period targets, not planned sets. **Deactivate** sends `PATCH` `{ "active": false }`. **Activate** turns that flag back on. The unit list comes from the exercise catalog.

## Calendar API

`GET /calendar` requires a Bearer token. It returns this user's sessions that have a `session_at`, ordered by that time. Unscheduled sessions are omitted. There are no generated weekday slots.

`from` and `to` are inclusive bounds on `session_at`. `from` later than `to` is **400**. Optional `plan_id` keeps only sessions on that plan. Another user's sessions never appear. A `plan_id` you do not own returns an empty list.

Each row is `id`, `name`, `session_at`, `status`, and `plan_id`.

## Ownership

Get, update, and delete for a session, plan, or goal load the row only when `user_id` matches the JWT user. A missing id and another user's id both return **404** with the same detail: `Session not found`, `Plan not found`, or `Goal not found`. These routes do not use **403**, so a caller cannot tell whether the id exists.

The same rule covers attaching or detaching a session on a plan, the source session of a clone, and an optional `plan_id` on a session write. Detach also returns `Session not found` when the session is not a member of that plan. List filters stay on the current user. `GET /sessions?plan_id=` for a plan you do not own is **200** with an empty list.

Repeat the two-account check from [docs/idor-demo.md](docs/idor-demo.md).

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
| `CORS_ORIGINS` | SPA allowlist (exact origins, comma-separated). Default `http://localhost:5173` — not `*`, not `127.0.0.1`, not Compose host `web`. Allows `GET`/`POST`/`PATCH`/`DELETE`/`OPTIONS` and `Authorization` / `Content-Type`. JWT uses Bearer headers, so `allow_credentials` is off. |
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

## TanStack Query

`QueryClientProvider` wraps the app in `frontend/src/main.tsx`. The dashboard at `/` loads `GET /health` with `useQuery`. Later screens should use the helpers in `frontend/src/api/queryKeys.ts` and invalidate the same key after a mutation.

| Key | Use |
| --- | --- |
| `['health']` | API health badge |
| `['sessions', filters]` | Session list. `filters` is `{ from, to, status, activityTypeId, unscheduled, planId }` |
| `['plans']` | Plan list |
| `['plans', id]` | One plan |
| `['calendar', from, to, planId]` | Dated sessions for a range. Use `null` when a bound or plan is omitted |
| `['activity-types']` | Exercise catalog for selectors |
| `['goals', active]` | Period goals. `active` is `true`, `false`, or `null` for every goal |
| `['sessions', 'detail', id]` | One session |

## Dashboard

`/` is the protected dashboard. It loads `GET /sessions?unscheduled=false` for the signed-in user and shows up to eight dated sessions, latest date first. Each card links to `/sessions/:id`. When there are none, the page says **Create your first session**. Unscheduled sessions are left off this list. A failed load or a forbidden response shows an error banner.

## Sessions list

`/sessions` is behind the same login gate as `/`. It loads `GET /sessions` for the current user and sends filters as query parameters: `from`, `to` (local-day bounds), `status`, `unscheduled`, `plan_id`, and `activity_type_id`. The API omits other users' rows. **New session** opens `/sessions/new`. **Edit** opens `/sessions/:id`. With no sessions and no filters, the list says **Create your first session**. A failed load, a failed save, or a forbidden response shows an error banner.

The designer saves metadata plus ordered exercises. The activity selector lists system exercises and your custom types. Each option and the line under the control summarize that exercise's unit links (`name`, `unit_label`, and `per set` when the link says so). There is no `unit_hint`. The same selector filters the session list. Measurement fields come from that exercise's unit links, including a planned and an actual input. Either value can be left empty; a unit with both empty is omitted. Strength exercises (`per_set`) use numbered sets. Leave **When** empty to save `session_at` as null. **Plan** is optional.

**Save session** updates the open session. **Delete** asks for confirmation, then removes it. **Clone** asks for a copy name and date, calls `POST /sessions/{id}/clone`, and opens the new session. Planned values stay, actuals are cleared, and the plan is not copied. The copy says it is a snapshot, so editing the original afterward leaves the copy as it was. A missing or forbidden session shows **Session not found** or **You cannot change this session**. Saves, deletes, and clones refresh the session, plan, and calendar caches.

## Plans

`/plans` is behind the same login gate. Create a plan with a name and optional notes, start date, and length in weeks. Those two fields are labels only. Open a plan to edit or delete it. Deleting a plan leaves the sessions in your log. An empty list and failed saves or forbidden responses are shown on the page, not hidden.

Members are your sessions, attached and detached through `plan_id`. Dated sessions are listed earliest first. Unscheduled sessions are in a separate section. The attach list is `GET /sessions` for the current user, so another person's session cannot be chosen. Attaching a session that is already on another plan moves it.

## Calendar

`/calendar` is behind the same login gate. **Month** and **Week** load `GET /calendar` for the visible range. Only your dated sessions appear. An optional plan filter uses `plan_id`. Statuses are visually distinct. **Clone** on a session picks a date and calls `POST /sessions/{id}/clone`: planned values stay, actuals are cleared, and the plan is not copied. An empty range says so and links to **Create your first session**. A failed load or a forbidden clone shows an error banner. There is no Google Calendar sync.

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
