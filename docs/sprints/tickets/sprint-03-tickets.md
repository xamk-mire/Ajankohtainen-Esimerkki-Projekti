# Sprint 3 tickets — Sessions, clone, plans & calendar

Backlog for Sprint 3 ([index](../README.md)). Copy tickets into your issue tracker if you like; keep the IDs (`S3-01`, …) in branch and PR titles.

## Your task for Sprint 3

Sprint 2 staffed the membership desk and hung the **exercise** board. Members can walk in, but the **training floor** is still empty: no logbook, no program, no calendar, no private lockers.

Sprint 3 is where people actually train. Ship multi-exercise **WorkoutSessions** with **planned** and **actual** measurements, **session clone** for reuse, **WorkoutPlans** via `plan_id` on sessions (no junction table), an in-app **calendar**, and **period Goals** keyed by unit type. Talk about **sessions** and **measurements**, not a flat “workout” row. There is no `unit_hint` and **no** separate session-template feature.

Authentication got them through the door; **authorization** keeps User A from opening User B’s locker. Charts and the house coach still wait—you need an honest, private logbook first.

```text
UnitType ←→ ActivityType (exercise)     Sprint 2 catalog
                ↓
     WorkoutSessionItem → Measurement (planned_value, actual_value)
                ↓
          WorkoutSession ──plan_id──► WorkoutPlan
                │
                └── clone ──► new WorkoutSession (planned kept, actuals cleared)
```

**Teaching rules:**

- Activities are **individual exercises** (bench press, running, …).
- Reuse = **`POST /sessions/{id}/clone`** (deep snapshot). Editing the source does **not** change existing clones.
- Plans use **`workout_sessions.plan_id`**. There is **no** `workout_plan_sessions` table. Order members by **`session_at` ASC NULLS LAST**.
- Calendar is driven by **`session_at`** (optional `plan_id` filter)—not weekday placement rows.
- Period **Goals** (`unit_type_id`, week/month) are separate from planned set values.

### Prerequisites from Sprint 2

- JWT register / login / `me` and a protected React layout with token storage
- Alembic + models for `User`, `ActivityType`, `UnitType`, `activity_type_unit_types`
- Seeded **exercise-level** catalog (e.g. Running → duration + distance; Bench press → reps + weight `per_set`)
- Layered backend (`api` → `services` → `repositories` → `models`/`db`) and CORS allowlist

### What success looks like

1. Create a multi-exercise session with **planned** values (actuals empty or filled)
2. Assign it to a plan via **`plan_id`**; plan members ordered by `session_at`
3. **Clone** the session onto a date; planned kept, actuals cleared; fill actuals on the clone
4. Edit the source session (add an exercise)—the earlier clone is unchanged
5. Calendar month + week shows dated sessions; User B cannot open User A’s session/plan/calendar/goal
6. Dashboard shows recent sessions for the logged-in user only
7. Short IDOR demo write-up exists

**Suggested demo flow:** log in as A → create “Pull A” with planned sets → set `plan_id` → clone onto Monday → fill actuals → open Calendar → edit Pull A → confirm Monday clone unchanged → try B’s IDs (fail) → Dashboard.

### New tools & technologies

| Tool / technology | Role in this sprint |
| ----------------- | ------------------- |
| **TanStack Query** | Cache for sessions/plans/calendar |
| **Nested REST + Pydantic** | Items/measurements; clone body |
| **SQLAlchemy relationships** | Session → items → measurements; `plan_id` / `source_session_id` |
| **IDOR / object-level auth** | Ownership on every get/update/delete |
| **Calendar UI** | Month + week views over `session_at` |

### What you will learn

- Nested domain APIs with planned vs actual validation
- Clone-as-snapshot (no cascade)
- Plan membership without a junction table
- Calendar over dated sessions
- Ownership (IDOR) and TanStack Query list/forms

### Layered backend

```text
api/sessions.py        → services/sessions.py        → repositories/session.py
api/plans.py           → services/plans.py           → repositories/plan.py
api/calendar.py        → services/calendar.py        → (reuse the session repository)
api/goals.py           → services/goals.py           → repositories/goal.py
api/activity_types.py  → services/activity_types.py  → repositories/activity_type.py
                           services/ownership.py      (load a session, plan, or goal for the current user)
```

**Naming:** SQLAlchemy `Session` (the database unit of work) is not `WorkoutSession` (the domain row). Use `db: Session` for the ORM session and `WorkoutSession` for a training log entry.

| Put this here | Not here |
| ------------- | -------- |
| HTTP status codes, query parameters, `Depends(get_current_user)` | `api/` only |
| Planned/actual rules, clone snapshot, ownership checks | `services/` |
| Filtered `SELECT`s scoped by `user_id` | `repositories/` |
| `WorkoutSession`, `WorkoutPlan`, `Goal` tables | `models/` |
| Request and response bodies | `schemas/` |

### Out of scope

| Topic | When |
| ----- | ---- |
| Progress charts / aggregations | Sprint 4 |
| AI insights | Sprint 5 |
| Full automated test suite | Sprint 6 (optional) |
| Google Calendar sync / invites | Never Must |
| `session_templates` / `is_template` / `workout_plan_sessions` | **Do not build** |

### Week-by-week map

| Week | Focus | Ticket IDs | Checkpoint |
| ---- | ----- | ---------- | ---------- |
| **1** | Models + APIs (sessions, clone, plans, calendar, ownership) | S3-01 … S3-12 | OpenAPI happy path + IDOR fails |
| **2** | TanStack Query + session UI + clone in UI | S3-13 … S3-17 | Designer + clone from UI |
| **3** | Plans UI, calendar UI, dashboard, IDOR docs | S3-18 … S3-23 | Two-account + calendar demo |

### How the tickets fit together

```text
Week 1                              Week 2                         Week 3
────────                            ────────                       ────────
Session, item, measurement models   TanStack Query + API client    Plans list and detail
Goal + plan models (plan_id)        Sessions list and filters      Calendar month + week
Sessions CRUD + planned/actual      Session designer               Dashboard recent sessions
Filters, clone, plans, goals        Edit, delete, and clone        Empty and error states
Ownership (404) + calendar API      Activity type selector         IDOR demo write-up
                                                                   Period goals UI (stretch)
```

Concepts from Sprint 2 (JWT, the exercise catalog, Alembic, the layered packages, and the protected React layout) are assumed. This file focuses on the **training log**, **clone**, **plans**, **calendar**, and **ownership**.

Do **Must** tickets first, then **Should** (S3-21), then **Stretch** if you have time.

**How to read each ticket:** **New here** explains the concept and lists **Docs & tutorials**. **Your task** states the deliverable. **Instructions** walk through the work. **Stay in scope** keeps later tickets out of this one. **Commit** means create a new Git commit when the ticket is done (ticket ID in the message).

### Ticket index

| ID                                                                     | Title                                    | Week | Priority | Estimate |
| ---------------------------------------------------------------------- | ---------------------------------------- | ---- | -------- | -------- |
| [S3-01](#s3-01--session-models-and-migration)                          | Session models and migration             | 1    | Must     | L        |
| [S3-02](#s3-02--goal-model-and-migration)                              | Goal model and migration                 | 1    | Must     | M        |
| [S3-03](#s3-03--plan-model-and-migration)                              | Plan model and migration                 | 1    | Must     | M        |
| [S3-04](#s3-04--sessions-crud-api)                                     | Sessions CRUD API                        | 1    | Must     | L        |
| [S3-05](#s3-05--session-measurements-planned-and-actual)               | Session measurements (planned/actual)    | 1    | Must     | L        |
| [S3-06](#s3-06--session-filters)                                       | Session filters                          | 1    | Must     | M        |
| [S3-07](#s3-07--clone-session-api)                                     | Clone session API                        | 1    | Must     | L        |
| [S3-08](#s3-08--plans-crud-and-attach-api)                             | Plans CRUD and attach API                | 1    | Must     | L        |
| [S3-09](#s3-09--activity-types-api)                                    | Activity types API                       | 1    | Must     | M        |
| [S3-10](#s3-10--goals-crud-api)                                        | Goals CRUD API                           | 1    | Must     | M        |
| [S3-11](#s3-11--ownership-enforcement)                                 | Ownership enforcement                    | 1    | Must     | M        |
| [S3-12](#s3-12--calendar-api)                                          | Calendar API                             | 1    | Must     | M        |
| [S3-13](#s3-13--tanstack-query-setup)                                  | TanStack Query setup                     | 2    | Must     | S        |
| [S3-14](#s3-14--sessions-list-and-filters-ui)                          | Sessions list and filters UI             | 2    | Must     | L        |
| [S3-15](#s3-15--session-designer-planned-and-actual)                   | Session designer (planned + actual)      | 2    | Must     | L        |
| [S3-16](#s3-16--edit-delete-and-clone-session-ui)                      | Edit, delete, and clone session UI       | 2    | Must     | M        |
| [S3-17](#s3-17--activity-type-selector)                                | Activity type selector                   | 2    | Must     | M        |
| [S3-18](#s3-18--plans-ui)                                              | Plans UI                                 | 3    | Must     | L        |
| [S3-19](#s3-19--calendar-ui)                                           | Calendar UI (month + week)               | 3    | Must     | L        |
| [S3-20](#s3-20--dashboard-recent-sessions)                             | Dashboard recent sessions                | 3    | Must     | M        |
| [S3-21](#s3-21--empty-and-error-states)                                | Empty and error states                   | 3    | Should   | S        |
| [S3-22](#s3-22--idor-demo-documentation)                               | IDOR demo documentation                  | 3    | Must     | S        |
| [S3-23](#s3-23--optional-goals-ui)                                     | Optional Goals UI                        | 3    | Stretch  | M        |
| [S3-S1](#s3-s1--pagination)                                            | Pagination                               | —    | Stretch  | S        |
| [S3-S2](#s3-s2--ownership-api-tests)                                   | Ownership API tests                      | —    | Stretch  | M        |
| [S3-S3](#s3-s3--add-models-to-sqladmin)                                | Add models to SQLAdmin                   | —    | Stretch  | S        |
| [S3-S4](#s3-s4--planned-vs-actual-adherence-preview)                   | Planned vs actual adherence preview      | —    | Stretch  | M        |

---

## S3-01 — Session models and migration

| Field          | Value                |
| -------------- | -------------------- |
| **Type**       | feature              |
| **Week**       | 1                    |
| **Priority**   | Must                 |
| **Estimate**   | L                    |
| **Depends on** | Sprint 2 complete    |

### New here: sessions with planned and actual measurements

A **WorkoutSession** is one training outing. It can also sit unscheduled (`session_at` null) until someone puts it on a date. Each outing holds several **exercises** (`WorkoutSessionItem`). Each exercise holds **measurements**. A measurement stores **`planned_value`** and **`actual_value`** as separate nullable decimals. There is no single `value` column and no `unit_hint`.

`source_session_id` records which session a clone came from. Leave `plan_id` for S3-03: `workout_plans` does not exist yet, so this migration cannot add a real foreign key to it.

| Table | Columns to include |
| ----- | ------------------ |
| `workout_sessions` | `id`, `user_id` → `users.id` (ON DELETE CASCADE), `name`, `session_at` (timezone-aware, nullable), `status` (default `planned`), `notes`, `intensity` (nullable), `source_session_id` (nullable self-FK, ON DELETE SET NULL), `created_at`, `updated_at` |
| `workout_session_items` | `id`, `session_id` (ON DELETE CASCADE), `activity_type_id` (ON DELETE RESTRICT), `sort_order`, `notes` |
| `workout_session_measurements` | `id`, `session_item_id` (ON DELETE CASCADE), `unit_type_id` (ON DELETE RESTRICT), `planned_value` and `actual_value` as nullable `Numeric(12, 3)`, `set_index` (nullable integer) |

**Docs & tutorials:**

- [SQLAlchemy relationships](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html) — one-to-many and self-referential foreign keys
- [Constraints and indexes](https://docs.sqlalchemy.org/en/20/core/constraints.html) — `CheckConstraint` and `Index`
- [Alembic — create a revision](https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script) — a new revision after the Sprint 2 migration

### Your task

Add the three ORM models and one Alembic revision so a training log can store exercises and both planned and actual numbers. Later tickets attach plans, validate units, and clone rows. Your deliverable is the tables above, with status and intensity checks, and **without** `plan_id` yet.

### Instructions

1. Add `WorkoutSession`, `WorkoutSessionItem`, and `WorkoutSessionMeasurement` under `backend/app/models/`. Export them from `backend/app/models/__init__.py` so Alembic’s metadata includes them.
2. Map the columns in the table above. Use timezone-aware datetimes. Give measurements `Numeric(12, 3)` for both value columns.
3. Add relationships: a session owns items (`cascade="all, delete-orphan"`, ordered by `sort_order`); an item owns measurements (same cascade, ordered by `set_index`). `source_session_id` points at another `WorkoutSession`.
4. Constrain `status` to `planned`, `in_progress`, or `completed`. Constrain `intensity` to null or an integer from 1 to 10.
5. Index `(user_id, session_at)`. The `(plan_id, session_at)` index waits until S3-03 adds `plan_id`.
6. Create a revision that revises the Sprint 2 head (the catalog migration). A clear revision id such as `s301_sessions` is enough. Comment in the file that `plan_id` is added in S3-03.
7. Check your work: `alembic upgrade head` on a fresh database creates the three tables. `\d workout_session_measurements` (or the SQLAdmin/psql equivalent) shows `planned_value` and `actual_value`, and no `value` column.

### Stay in scope

- Leave `workout_plans` and `plan_id` for S3-03.
- Leave session HTTP routes for S3-04 and measurement validation for S3-05.
- Leave clone behavior for S3-07. The `source_session_id` column is enough here.

### Hints

- Import the model modules before you autogenerate, or write the revision by hand. Empty metadata produces an empty migration.
- Deleting a session should delete its items and measurements (`ON DELETE CASCADE`). Deleting an activity type that is still used should fail (`ON DELETE RESTRICT`).
- Skip `is_template`, a template table, and `workout_plan_sessions`.

### Acceptance criteria

- [ ] The migration applies on a fresh database after the Sprint 2 revision
- [ ] Measurements have separate `planned_value` and `actual_value` columns
- [ ] Status and intensity are enforced in the database
- [ ] `plan_id` is absent from this revision
- [ ] There is no template flag and no `workout_plan_sessions` table

### Suggested paths

`backend/app/models/workout_session.py`, `backend/app/models/workout_session_item.py`, `backend/app/models/workout_session_measurement.py`, `backend/alembic/versions/`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-01` in the message, for example `S3-01: short summary`. Never commit `.env` or secrets.

---

## S3-02 — Goal model and migration

| Field          | Value                      |
| -------------- | -------------------------- |
| **Type**       | feature                    |
| **Week**       | 1                          |
| **Priority**   | Must                       |
| **Estimate**   | M                          |
| **Depends on** | S3-01 (same batch is fine) |

### New here: period goals

A **Goal** is a target for a stretch of time: “run 20 km this week” or “bench 5000 kg this month.” It points at a **`unit_type_id`** and, optionally, one **`activity_type_id`**. Sprint 5’s coach reads these rows. They are separate from `planned_value` on a set inside a session.

`period` is only `week` or `month`. `active` lets a member pause a goal without deleting it.

**Docs & tutorials:**

- [SQLAlchemy — CheckConstraint](https://docs.sqlalchemy.org/en/20/core/constraints.html#check-constraint) — limit `period` in the database
- [Alembic — create a revision](https://alembic.sqlalchemy.org/en/latest/tutorial.html#create-a-migration-script) — chain this revision after S3-01

### Your task

Add a `goals` table and ORM model so each user can store period targets by unit. The HTTP API waits until S3-10, and the page waits until S3-23. Your deliverable is the model, the foreign keys, and a `period` check constraint.

### Instructions

1. Add `backend/app/models/goal.py` with columns: `id`, `user_id` → `users.id` (ON DELETE CASCADE), `unit_type_id` → `unit_types.id` (ON DELETE RESTRICT), `activity_type_id` nullable → `activity_types.id` (ON DELETE SET NULL is fine), `target_value` (numeric, required), `period`, `active` (boolean, default true), `created_at`.
2. Add a check constraint so `period` is only `week` or `month`.
3. Export the model and add a revision after the session migration (for example `s302_goals`).
4. Check your work: after `alembic upgrade head`, inserting `period='year'` fails, and a goal row can exist with `activity_type_id` null.

### Stay in scope

- Leave `/goals` routes for S3-10 and the Goals page for S3-23.
- Leave `planned_value` / `actual_value` on session measurements. A goal is a period target.

### Hints

- A short docstring on the model that separates goals from planned set values saves a later mix-up.
- Keep the table small. Charts that sum actuals against the target belong to Sprint 4.

### Acceptance criteria

- [ ] `goals` migrates after the session tables
- [ ] `period` is constrained to `week` or `month`
- [ ] `activity_type_id` may be null; `unit_type_id` may not
- [ ] The model is exported with the other ORM classes

### Suggested paths

`backend/app/models/goal.py`, `backend/alembic/versions/`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-02` in the message, for example `S3-02: short summary`. Never commit `.env` or secrets.

---

## S3-03 — Plan model and migration

| Field          | Value   |
| -------------- | ------- |
| **Type**       | feature |
| **Week**       | 1       |
| **Priority**   | Must    |
| **Estimate**   | M       |
| **Depends on** | S3-01   |

### New here: plans without a junction

A **WorkoutPlan** is a named program (“Pull block”, “March base”). A session belongs to a plan through **`workout_sessions.plan_id`**. One session has at most one plan. Deleting the plan sets that column to null (`ON DELETE SET NULL`) and leaves the session in the log.

`start_date` and `length_weeks` are labels for the program. They do not generate weeks, weekdays, or extra session rows. Order the plan’s sessions by **`session_at` ascending, nulls last**, so dated days come first and unscheduled sessions sit at the end.

**Docs & tutorials:**

- [SQLAlchemy relationships](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html) — many sessions, one plan
- [PostgreSQL NULLS FIRST / LAST](https://www.postgresql.org/docs/current/queries-order.html) — `NULLS LAST` with `ORDER BY session_at`
- [Alembic operations](https://alembic.sqlalchemy.org/en/latest/ops.html) — `add_column` and `create_index` on an existing table

### Your task

Add `workout_plans` and the missing `plan_id` on `workout_sessions`. Membership is that foreign key alone. Your deliverable is the plan model, the column, the index, and a relationship that lists members by `session_at`.

### Instructions

1. Add `backend/app/models/workout_plan.py` with `id`, `user_id` → `users.id` (ON DELETE CASCADE), `name`, `notes`, optional `start_date`, optional `length_weeks`, `created_at`, and `updated_at`.
2. In the same revision (for example `s303_plans`, after the goals revision), add nullable `plan_id` on `workout_sessions` with a foreign key to `workout_plans.id` and `ON DELETE SET NULL`.
3. Index `(plan_id, session_at)`.
4. Relationship: `WorkoutPlan.sessions` ordered by `session_at` ascending, nulls last. `WorkoutSession.plan` points back. A session’s `plan_id` is a single nullable id.
5. Check your work: upgrade head, create a plan, set `plan_id` on two sessions (one dated, one with `session_at` null), and confirm the plan’s session collection returns the dated row first. Confirm `workout_plan_sessions` was not created.

### Stay in scope

- Leave plan HTTP routes and attach/detach for S3-08.
- Leave the calendar for S3-12 and S3-19. `start_date` does not place sessions on days.

### Hints

- If you autogenerate, confirm the revision alters `workout_sessions` and creates `workout_plans`. It should not create a link table.
- Note on the model that one session belongs to at most one plan.

### Acceptance criteria

- [ ] `workout_plans` exists and migrates after goals
- [ ] `workout_sessions.plan_id` is a nullable FK with ON DELETE SET NULL
- [ ] `(plan_id, session_at)` is indexed
- [ ] Loading a plan’s sessions orders by `session_at` ascending, nulls last
- [ ] There is no `workout_plan_sessions` table

### Suggested paths

`backend/app/models/workout_plan.py`, `backend/app/models/workout_session.py`, `backend/alembic/versions/`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-03` in the message, for example `S3-03: short summary`. Never commit `.env` or secrets.

---

## S3-04 — Sessions CRUD API

| Field          | Value        |
| -------------- | ------------ |
| **Type**       | feature      |
| **Week**       | 1            |
| **Priority**   | Must         |
| **Estimate**   | L            |
| **Depends on** | S3-01, JWT   |

### New here: nested session payloads

A session is one resource with a tree inside it: exercises, and measurements on those exercises. Create and update send that tree in one JSON body. There are no separate `/items` or `/measurements` routes in this sprint.

Every route requires the JWT from Sprint 2 (`get_current_user`). A missing or invalid token is **401**. A session id that does not exist, or that belongs to someone else, is **404** with detail `Session not found`. Use the same detail for both cases so a caller cannot tell them apart. S3-11 centralizes that check; call it from this ticket if you already have it, or filter `user_id` in the repository and raise the same 404 until S3-11 lands.

List results are ordered by `created_at` descending (newest first).

**Docs & tutorials:**

- [FastAPI — nested models](https://fastapi.tiangolo.com/tutorial/body-nested-models/) — items and measurements in one body
- [FastAPI — dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) — `get_db` and `get_current_user`
- [FastAPI — handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) — 401, 404, and 422
- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/) — request and response schemas

### Your task

Ship owner-scoped session CRUD that round-trips a nested exercise list. Your deliverable is `GET/POST /sessions` and `GET/PATCH/DELETE /sessions/{id}`, with schemas, a service, and a repository. Optional `plan_id` on create and update must refer to a plan the caller owns.

### Instructions

1. Add `backend/app/schemas/session.py` with write and read shapes. A session has `name` (required, 1–200 characters), optional `session_at`, `status` (`planned` \| `in_progress` \| `completed`, default `planned`), `notes`, `intensity` (1–10 or null), optional `plan_id`, and `items`. Each item has `activity_type_id`, `sort_order`, `notes`, and `measurements`. Each measurement has `unit_type_id`, `planned_value`, `actual_value`, and optional `set_index` (≥ 0). The read model includes ids, `user_id`, `source_session_id`, timestamps, and the nested tree.
2. Add `backend/app/repositories/session.py` to load and list sessions for a `user_id`, with items and measurements eager-loaded. List order is `created_at` descending.
3. Add `backend/app/services/sessions.py` for create, get, update, and delete. Set `user_id` from the current user, never from the body. If `plan_id` is set, load that plan for the same user or return **404** `Plan not found`.
4. On update, only change fields the client sent. When `items` is present, replace the whole exercise tree (clear and rebuild) so the saved session matches the payload. Reject JSON `null` for required fields such as `name` and `status` with **422**.
5. Add `backend/app/api/sessions.py` and include the router in `backend/app/main.py`:
   - `GET /sessions` → the caller’s sessions
   - `POST /sessions` → **201** and the created session
   - `GET /sessions/{session_id}` → one session
   - `PATCH /sessions/{session_id}` → the updated session
   - `DELETE /sessions/{session_id}` → **204**
6. Check your work in OpenAPI: register, create a session with one exercise, GET it back, PATCH the name, DELETE it. Repeat GET and DELETE with another user’s id and confirm **404** `Session not found`. Call the routes with no token and confirm **401**.

### Stay in scope

- Leave catalog checks (allowed units, `per_set` / `set_index`, “both values empty”) for S3-05.
- Leave query filters for S3-06 and clone for S3-07.
- Leave pagination (`page` / `limit`) for S3-S1. This list may return every matching row.

### Hints

- Name the ORM class `WorkoutSession` and the FastAPI dependency `db: Session` so the two “sessions” stay distinct in signatures.
- Eager-load items and measurements on read, or the response will be empty after the session closes.

### Acceptance criteria

- [ ] The owner can create, read, update, and delete a session in OpenAPI
- [ ] Nested items and measurements round-trip on GET
- [ ] `plan_id` must be the caller’s plan; another user’s plan is **404** `Plan not found`
- [ ] Another user’s session id is **404** `Session not found` on get, update, and delete
- [ ] Missing JWT is **401**
- [ ] `GET /sessions` returns only the caller’s rows, newest `created_at` first

### Suggested paths

`backend/app/api/sessions.py`, `backend/app/services/sessions.py`, `backend/app/repositories/session.py`, `backend/app/schemas/session.py`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-04` in the message, for example `S3-04: short summary`. Never commit `.env` or secrets.

---

## S3-05 — Session measurements (planned and actual)

| Field          | Value                    |
| -------------- | ------------------------ |
| **Type**       | feature                  |
| **Week**       | 1                        |
| **Priority**   | Must                     |
| **Estimate**   | L                        |
| **Depends on** | S3-04, Sprint 2 unit links |

### New here: planned vs actual

Each measurement may carry **`planned_value`**, **`actual_value`**, or both. Reject a payload where **both are null** (422, for example `Measurement needs a planned value, an actual value, or both`). The unit must be one of the activity’s Sprint 2 links. If that link is `per_set`, `set_index` is required (422, for example `set_index is required for per-set units`). A unit that is not linked is rejected (422, for example `Unit is not allowed for this activity`).

Session-level units (`per_set` false) may omit `set_index`. Clone (S3-07) will copy `planned_value` and clear `actual_value`; this ticket only stores and validates the pair.

**Docs & tutorials:**

- [FastAPI — nested models](https://fastapi.tiangolo.com/tutorial/body-nested-models/) — measurements inside items
- [Pydantic fields](https://docs.pydantic.dev/latest/concepts/fields/) — optional decimals and `set_index >= 0`
- Sprint 2 catalog: `activity_type_unit_types.per_set` is the flag you check

### Your task

Validate and persist planned and actual values on session create and update, and return them on GET. Your deliverable is service-layer checks against the activity’s unit links, still on the nested session body from S3-04.

### Instructions

1. Keep measurements nested on the session write schema from S3-04 (`planned_value`, `actual_value`, `unit_type_id`, `set_index`). Do not add measurement routes.
2. In the session service, when building each item, load the activity type. If it does not exist, fail the request (422).
3. For each measurement, require at least one of `planned_value` and `actual_value`.
4. Look up the activity↔unit link (the Sprint 2 association). Missing link → 422. When the link has `per_set` true and `set_index` is missing → 422. When `per_set` is false, `set_index` may be omitted.
5. Save both decimals as sent, including a null on the side the client left empty.
6. Check your work in OpenAPI with the seeded catalog:
   - Bench press: reps + weight with `set_index` 0, planned only → 201, GET shows `actual_value` null
   - The same unit with actual only, and with both values, succeeds
   - Both values null → 422
   - A unit that Running does not allow (for example weight on a run) → 422
   - A per-set unit with no `set_index` → 422

### Stay in scope

- Leave the designer UI for S3-15.
- Leave clone’s “copy planned, clear actual” behavior for S3-07. Document that contract in a short comment near the measurement builder so S3-07 can follow it.

### Hints

- Validate in the service, where you can see the link row. A Pydantic model alone does not know which units an activity accepts.
- `set_index` starts at 0 for the first set.

### Acceptance criteria

- [ ] Planned-only, actual-only, and both-values measurements round-trip
- [ ] A measurement with both values null is 422
- [ ] A unit that is not linked to the activity is 422
- [ ] A per-set unit without `set_index` is 422
- [ ] A session-level unit may omit `set_index`

### Suggested paths

`backend/app/services/sessions.py`, `backend/app/schemas/session.py`, `backend/app/repositories/unit_type.py`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-05` in the message, for example `S3-05: short summary`. Never commit `.env` or secrets.

---

## S3-06 — Session filters

| Field          | Value   |
| -------------- | ------- |
| **Type**       | feature |
| **Week**       | 1       |
| **Priority**   | Must    |
| **Estimate**   | M       |
| **Depends on** | S3-04   |

### New here: list filters that cannot widen access

`GET /sessions` already returns the caller’s rows. Filters narrow that set. They are query parameters, always combined with `user_id`. A filter must not become a way to read someone else’s log.

| Query parameter | Behavior |
| --------------- | -------- |
| `from` | `session_at >= from`. Rows with null `session_at` drop out, because null is not inside a range |
| `to` | `session_at <= to` |
| `status` | exact status |
| `activity_type_id` | sessions that contain at least one item with that activity |
| `unscheduled` | `true` → `session_at` is null; `false` → `session_at` is set; omit the parameter → both |
| `plan_id` | sessions with that `plan_id` |

If `from` is later than `to`, return **400** with detail `from must not be after to`. If `plan_id` is another user’s plan, return **200** and an empty list. The list is still scoped by `user_id`, so you do not answer 404 for a filter the caller is not allowed to “see.”

**Docs & tutorials:**

- [FastAPI — query parameters](https://fastapi.tiangolo.com/tutorial/query-params/) — optional filters and aliases
- [FastAPI — handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) — 400 for a bad range
- [SQLAlchemy — filter](https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#the-where-clause) — combine predicates with the user id

### Your task

Add the filters above to `GET /sessions` and document them in OpenAPI. Your deliverable is a repository filter that always includes `user_id`, plus a 400 when the date range is backwards.

### Instructions

1. Accept the query names in the table. `from` and `to` are reserved-ish in Python, so bind them with an alias (`from` → a parameter such as `session_from`) while the URL keeps `from` and `to`.
2. Apply every provided filter in the repository together with `user_id`. Keep the S3-04 order: `created_at` descending.
3. Validate `from <= to` before querying. A reversed range is 400 `from must not be after to`.
4. `unscheduled=true` ignores the idea of a date range for those rows (they have no `session_at`). When the client sends `unscheduled=true`, do not also require a date match.
5. Check your work in OpenAPI: the parameter list shows `from`, `to`, `status`, `activity_type_id`, `unscheduled`, and `plan_id`. A session outside the range disappears. Another user’s `plan_id` returns `[]` with 200. Another user’s sessions never appear, even with a wide `from`/`to`.

### Stay in scope

- Leave `page` and `limit` for S3-S1.
- Leave `GET /calendar` for S3-12. Calendar reuses the same date and plan rules on dated rows only.

### Hints

- Declare the query parameters on the route so OpenAPI lists them. A free-form `dict` of filters will not show up in the docs.
- Compare timezone-aware datetimes. A date-only `from` should be the start of that day if you pass a date; the API itself takes datetimes.

### Acceptance criteria

- [ ] OpenAPI documents `from`, `to`, `status`, `activity_type_id`, `unscheduled`, and `plan_id`
- [ ] `from` after `to` returns 400 `from must not be after to`
- [ ] Filters only narrow the current user’s sessions
- [ ] A foreign `plan_id` returns an empty list, not another user’s rows and not 404

### Suggested paths

`backend/app/api/sessions.py`, `backend/app/repositories/session.py`, `backend/app/services/sessions.py`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-06` in the message, for example `S3-06: short summary`. Never commit `.env` or secrets.

---

## S3-07 — Clone session API

| Field          | Value   |
| -------------- | ------- |
| **Type**       | feature |
| **Week**       | 1       |
| **Priority**   | Must    |
| **Estimate**   | L       |
| **Depends on** | S3-05   |

### New here: clone as snapshot

`POST /sessions/{id}/clone` creates a **new** session owned by the caller. The clone is a deep copy: new session, item, and measurement ids. Later edits to the source do not change the clone, and edits to the clone do not change the source.

| Field | What the clone stores |
| ----- | --------------------- |
| Items | Same activity, `sort_order`, and notes; new row ids |
| Measurements | Same `planned_value` and `set_index`; **`actual_value` is null** |
| `status` | Always `planned` |
| `source_session_id` | The source session’s id |
| `name` | Body `name` if sent, otherwise the source name |
| `session_at` | Body `session_at` if sent, otherwise **null** (unscheduled). Do not copy the source date |
| `plan_id` | Body `plan_id` if sent (and the caller must own that plan), otherwise **null**. Do not copy the source plan |

The optional body is only `name`, `session_at`, and `plan_id`. A source the caller does not own is **404** `Session not found`, including when the id does not exist.

**Docs & tutorials:**

- [SQLAlchemy — cascades and copies](https://docs.sqlalchemy.org/en/20/orm/cascades.html) — build new rows; do not share the source’s item objects
- [FastAPI — request body](https://fastapi.tiangolo.com/tutorial/body/) — an optional clone body
- [REST — POST for a new resource](https://fastapi.tiangolo.com/tutorial/response-status-code/) — return **201** and the new session

### Your task

Implement clone in the session service and prove the copy is isolated. Your deliverable is `POST /sessions/{session_id}/clone` returning the new session, with planned values kept and actuals cleared.

### Instructions

1. Add a small clone schema (`name`, `session_at`, `plan_id`, all optional) and `POST /sessions/{session_id}/clone` → **201** plus the session read model.
2. Load the source with the S3-04/S3-11 ownership rule. Failure is 404 `Session not found`.
3. Insert a new `WorkoutSession` for `current_user` using the table above. Copy items and measurements as new rows. Clear every `actual_value`.
4. If the body includes `plan_id`, resolve it the same way as session create (404 `Plan not found` when it is missing or not owned). If the body omits `plan_id`, store null.
5. Check your work in OpenAPI:
   - Clone a session that has planned and actual values. The new id differs, `source_session_id` is the source, status is `planned`, actuals are null, planned values match, and `plan_id` is null when omitted.
   - PATCH the source (add an exercise or change a planned value). GET the clone again: it is unchanged.
   - Clone another user’s id → 404 `Session not found`.

### Stay in scope

- Leave the clone form in the UI for S3-16. The calendar’s “clone onto a date” action calls this same endpoint.
- Leave template tables and `is_template` out. Clone is the reuse mechanism.

### Hints

- Copy inside the service with new model instances. A shallow copy of the source object will alias the same items.
- Default `session_at` to null so “clone” and “place on Monday” stay separate. The client sends Monday when it wants a date.

### Acceptance criteria

- [ ] Clone returns 201, keeps `planned_value`, and sets `actual_value` to null
- [ ] `source_session_id` is the source id and `status` is `planned`
- [ ] Omitted `plan_id` and omitted `session_at` are stored as null
- [ ] Editing the source does not change the clone
- [ ] Cloning another user’s session returns 404 `Session not found`

### Suggested paths

`backend/app/api/sessions.py`, `backend/app/services/sessions.py`, `backend/app/schemas/session.py`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-07` in the message, for example `S3-07: short summary`. Never commit `.env` or secrets.

---

## S3-08 — Plans CRUD and attach API

| Field          | Value         |
| -------------- | ------------- |
| **Type**       | feature       |
| **Week**       | 1             |
| **Priority**   | Must          |
| **Estimate**   | L             |
| **Depends on** | S3-03, S3-04  |

### New here: attach by `plan_id`

Plan membership is the session’s `plan_id`. Create and edit the plan on `/plans`. Attach and detach with thin routes that set or clear that column:

- `POST /plans/{plan_id}/sessions/{session_id}` sets `session.plan_id` to this plan (a session already on another plan moves)
- `DELETE /plans/{plan_id}/sessions/{session_id}` clears `plan_id` when the session is on this plan

`GET /plans/{id}` returns the plan plus its sessions ordered by **`session_at` ascending, nulls last** (the S3-03 relationship). List plans newest `created_at` first. Deleting a plan uses the FK rule from S3-03: sessions remain, with `plan_id` null.

Missing plan, another user’s plan, missing session, or another user’s session → **404**. Use `Plan not found` for a bad plan id and `Session not found` for a bad session id. Detach of a session that is not on this plan is the same **404** `Session not found`.

**Docs & tutorials:**

- [FastAPI — path parameters](https://fastapi.tiangolo.com/tutorial/path-params/) — plan id and session id on the attach routes
- [SQLAlchemy — ordering relationship](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html) — the member list comes from the plan relationship
- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/) — a plan detail schema with a nested session summary

### Your task

Ship owner-scoped plan CRUD and attach/detach through `plan_id`. Your deliverable is the `/plans` router, service, repository, and schemas, with members ordered by `session_at`.

### Instructions

1. Schemas: create/update with `name` (required on create, 1–200 characters), optional `notes`, optional `start_date`, optional `length_weeks` (≥ 1). A plan read model includes ids and timestamps. Plan detail adds `sessions`: `id`, `name`, `session_at`, `status` — a summary, not the full measurement tree.
2. Repository: list the caller’s plans by `created_at` descending; load one plan with its sessions for the same `user_id`.
3. Service: create, get, update, delete, attach, detach. Reject clearing `name` to null on PATCH with 422. Attach loads both rows for `current_user`, then sets `plan_id`. Detach clears it only when it already equals this plan.
4. Routes, all behind JWT:
   - `GET /plans` → list
   - `POST /plans` → **201** and the detail
   - `GET /plans/{plan_id}` → detail
   - `PATCH /plans/{plan_id}` → detail
   - `DELETE /plans/{plan_id}` → **204**
   - `POST` and `DELETE /plans/{plan_id}/sessions/{session_id}` → the updated detail
5. Register the router in `main.py`.
6. Check your work: create a plan, attach two owned sessions (earlier date, later date, and one unscheduled), and confirm that order. Attach another user’s session → 404 `Session not found`. GET another user’s plan → 404 `Plan not found`. Delete the plan and confirm the sessions still exist with `plan_id` null.

### Stay in scope

- Leave the plans pages for S3-18.
- Leave weekday, `sequence`, and `week_offset` columns out. Order is `session_at`.
- Leave a junction table out.

### Hints

- Reuse the session ownership load from S3-04 so attach cannot grab a foreign session.
- `start_date` and `length_weeks` are stored and returned. They do not create child sessions.

### Acceptance criteria

- [ ] Plan CRUD works for the owner and returns 401 without a token
- [ ] Attach and detach change `plan_id` only
- [ ] Plan detail lists members by `session_at` ascending, nulls last
- [ ] Another user’s plan or session id returns 404 with `Plan not found` or `Session not found`
- [ ] There is still no `workout_plan_sessions` table

### Suggested paths

`backend/app/api/plans.py`, `backend/app/services/plans.py`, `backend/app/repositories/plan.py`, `backend/app/schemas/plan.py`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-08` in the message, for example `S3-08: short summary`. Never commit `.env` or secrets.

---

## S3-09 — Activity types API

| Field          | Value              |
| -------------- | ------------------ |
| **Type**       | feature            |
| **Week**       | 1                  |
| **Priority**   | Must               |
| **Estimate**   | M                  |
| **Depends on** | Sprint 2 catalog   |

### New here: the exercise catalog over HTTP

Sprint 2 seeded system exercises and their unit links in the database. The session designer needs that catalog from the API: system rows (`user_id` null) plus custom exercises owned by the caller. Each exercise includes its **unit links** (`unit_type_id`, `sort_order`, `is_required`, `per_set`, and the unit’s name, slug, and label). There is no `unit_hint` field.

Custom create is allowed. The caller sends `name`, an optional `slug`, and at least one unit link. If `slug` is omitted, derive one from the name (lowercase, non-alphanumerics become `_`). A slug the caller already uses returns **409** (for example `Activity type slug already exists`). An unknown `unit_type_id`, or the same unit twice in one body, returns **422**.

**Docs & tutorials:**

- [FastAPI — response model](https://fastapi.tiangolo.com/tutorial/response-model/) — return links without leaking other users’ custom rows
- [Pydantic validators](https://docs.pydantic.dev/latest/concepts/validators/) — slug shape: lowercase letters, digits, underscores
- Sprint 2 `activity_type_unit_types` — `per_set` is what the designer uses to draw sets

### Your task

Expose the exercise catalog to the logged-in user, including unit links, and allow a custom exercise scoped to that user. Your deliverable is `GET /activity-types` and `POST /activity-types`.

### Instructions

1. Add schemas for a unit link (read and write) and an activity type read model: `id`, `name`, `slug`, `is_system`, `user_id`, `unit_links`.
2. Repository: list system types plus rows with `user_id` equal to the caller. Load unit links and the related unit type. A custom type owned by someone else stays out of the list.
3. Service: list those rows. Create sets `user_id` to the caller and `is_system` false. Normalize or generate the slug. Reject a duplicate slug for that user with 409. Reject an unknown unit or a repeated unit in `unit_links` with 422.
4. Routes behind JWT: `GET /activity-types` → the list; `POST /activity-types` → **201** and the created type. Register the router.
5. Check your work: the seeded Running and Bench press rows appear with their links (`per_set` true on bench reps/weight). A second user does not see the first user’s custom exercise. Posting the same slug again returns 409.

### Stay in scope

- Leave the selector component for S3-17. This ticket is the JSON the selector will call.
- Leave edits and deletes of activity types out. List and create are enough.
- Leave SQLAdmin catalog screens as they are from Sprint 2.

### Hints

- `is_system` can be derived (`user_id is None`) so the UI can group “Exercises” and “Your exercises.”
- Return units in `sort_order` so the designer lays out duration before distance, or reps before weight, the way the seed defined them.

### Acceptance criteria

- [ ] `GET /activity-types` returns system exercises and the caller’s custom exercises, with unit links
- [ ] Another user’s custom exercise is absent
- [ ] `POST` creates a custom exercise for the caller and returns 201
- [ ] Duplicate slug for that user is 409; an unknown unit is 422
- [ ] Unauthenticated calls are 401

### Suggested paths

`backend/app/api/activity_types.py`, `backend/app/services/activity_types.py`, `backend/app/repositories/activity_type.py`, `backend/app/schemas/activity_type.py`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-09` in the message, for example `S3-09: short summary`. Never commit `.env` or secrets.

---

## S3-10 — Goals CRUD API

| Field          | Value   |
| -------------- | ------- |
| **Type**       | feature |
| **Week**       | 1       |
| **Priority**   | Must    |
| **Estimate**   | M       |
| **Depends on** | S3-02   |

### New here: goals as their own resource

Period goals are small JSON documents, separate from session measurements. The UI is optional (S3-23). The API is required so ownership and Sprint 5 have something to call.

A goal body has `unit_type_id` (must exist), optional `activity_type_id` (must be a system exercise or one of the caller’s custom exercises), `target_value` (greater than 0), `period` (`week` or `month`), and `active` (default true). List accepts an optional `active` query flag. Newest `created_at` first.

A missing or foreign goal is **404** `Goal not found`.

**Docs & tutorials:**

- [FastAPI — query parameters](https://fastapi.tiangolo.com/tutorial/query-params/) — optional `active` filter
- [Pydantic constrained types](https://docs.pydantic.dev/latest/concepts/fields/) — `target_value` greater than 0
- [FastAPI — handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) — 404 vs 422

### Your task

Add owner-scoped `/goals` CRUD that validates the unit and the optional activity. Your deliverable is the router, service, repository, and schemas. The page can wait.

### Instructions

1. Schemas: create, update, and read matching the columns from S3-02. `target_value` must be greater than 0. `period` is `week` or `month`.
2. Repository: list and get by `user_id`. Optional `active` filter when the query parameter is present. Order by `created_at` descending.
3. Service: on write, reject an unknown `unit_type_id` with 422. If `activity_type_id` is set, it must be visible to the caller (system or their custom type); otherwise 422. Set `user_id` from the token.
4. Routes behind JWT:
   - `GET /goals` (optional `active`)
   - `POST /goals` → **201**
   - `GET /goals/{goal_id}`
   - `PATCH /goals/{goal_id}`
   - `DELETE /goals/{goal_id}` → **204**
5. Register the router. Check your work: create a week goal against a seeded unit, list it, set `active` false, and confirm another user’s id returns 404 `Goal not found`. A `target_value` of 0 is 422.

### Stay in scope

- Leave the Goals page for S3-23.
- Leave progress charts that compare actuals to `target_value` for Sprint 4.
- A goal is not a planned set. Do not write `planned_value` from this API.

### Hints

- Reuse the activity-type visibility rule from S3-09 so a goal cannot point at someone else’s custom exercise.
- PATCH should allow toggling `active` without resending every field.

### Acceptance criteria

- [ ] The owner can create, list, read, update, and delete goals
- [ ] `unit_type_id` is validated; optional `activity_type_id` must be visible to the caller
- [ ] `target_value` must be greater than 0 and `period` must be `week` or `month`
- [ ] `GET /goals?active=` filters; omitted `active` returns both
- [ ] Another user’s goal id is 404 `Goal not found`; missing JWT is 401

### Suggested paths

`backend/app/api/goals.py`, `backend/app/services/goals.py`, `backend/app/repositories/goal.py`, `backend/app/schemas/goal.py`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-10` in the message, for example `S3-10: short summary`. Never commit `.env` or secrets.

---

## S3-11 — Ownership enforcement

| Field          | Value                 |
| -------------- | --------------------- |
| **Type**       | feature               |
| **Week**       | 1                     |
| **Priority**   | Must                  |
| **Estimate**   | M                     |
| **Depends on** | S3-04, S3-08, S3-10   |

### New here: IDOR

**IDOR** (insecure direct object reference) is what happens when a route trusts an id from the URL and forgets to check the owner. User B pastes User A’s session id and reads A’s log. Authentication already proved who is calling. This ticket is **authorization**: the row must belong to that caller.

Use one convention everywhere:

| Situation | Status | Detail |
| --------- | ------ | ------ |
| Missing or invalid JWT | 401 | the Sprint 2 auth message (for example `Could not validate credentials`) |
| Session id missing or owned by someone else | 404 | `Session not found` |
| Plan id missing or owned by someone else | 404 | `Plan not found` |
| Goal id missing or owned by someone else | 404 | `Goal not found` |

The same detail for “missing” and “someone else’s” means the API does not reveal which ids exist. Do not return 403 for these object lookups. Apply the check on get, update, delete, clone’s source session, and plan attach/detach.

**Docs & tutorials:**

- [OWASP — testing for IDOR](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References) — why the id in the URL is not proof of ownership
- [FastAPI — dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) — one helper the routes call
- [FastAPI — HTTPException](https://fastapi.tiangolo.com/tutorial/handling-errors/#use-httpexception) — map a domain “not found” error to 404

### Your task

Centralize “load this session, plan, or goal for the current user, or raise.” Your deliverable is one ownership module used by the session, plan, and goal services, with the 404 details in the table. S3-22 will document the demo; this ticket makes the demo true.

### Instructions

1. Add `backend/app/services/ownership.py` with loaders for a session, a plan, a plan-with-sessions, and a goal. Each loader takes `db`, the id, and `user_id`, uses the repository `get_*_for_user` query, and raises a small domain error when the row is missing (`SessionNotFoundError`, `PlanNotFoundError`, `GoalNotFoundError`).
2. Map those errors in the routers to 404 and the details in the table. Keep 401 on the auth dependency.
3. Replace ad-hoc lookups in session get/update/delete, clone, plan get/update/delete/attach/detach, and goal get/update/delete so they go through these loaders. Create still sets `user_id` from the token. List endpoints stay filtered by `user_id` and do not 404 when a filter matches nothing.
4. When a session write references `plan_id`, the plan loader’s failure stays `Plan not found`.
5. Check your work with two tokens: A creates a session, a plan, and a goal. B calls GET, PATCH, and DELETE on those ids, plus clone and attach. Every one of those calls is 404 with the matching detail. A random UUID returns the same detail as B’s attempt on A’s id.

### Stay in scope

- Leave the written demo script for S3-22 and automated tests for S3-S2.
- Leave list and calendar aggregation for their own tickets. This ticket is object-level get/update/delete (and clone/attach).
- A foreign `plan_id` **filter** on `GET /sessions` stays an empty 200, as in S3-06. That is a filter, not an object fetch.

### Hints

- Put the `user_id` predicate in the repository query (`WHERE id = :id AND user_id = :user_id`). Checking `row.user_id` after a global `get(id)` is easy to forget on the next route.
- Re-export the not-found errors from the feature services if that keeps router imports tidy. The rule itself lives in `ownership.py`.

### Acceptance criteria

- [ ] Cross-user get, update, and delete fail for sessions, plans, and goals with 404 and the details above
- [ ] Clone of another user’s session and attach of another user’s session fail the same way
- [ ] A missing id and a foreign id return the same status and detail
- [ ] Missing JWT remains 401
- [ ] The convention is the one S3-22 will write down (404, not 403, for object ids)

### Suggested paths

`backend/app/services/ownership.py`, `backend/app/services/sessions.py`, `backend/app/services/plans.py`, `backend/app/services/goals.py`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-11` in the message, for example `S3-11: short summary`. Never commit `.env` or secrets.

---

## S3-12 — Calendar API

| Field          | Value         |
| -------------- | ------------- |
| **Type**       | feature       |
| **Week**       | 1             |
| **Priority**   | Must          |
| **Estimate**   | M             |
| **Depends on** | S3-04, S3-06  |

### New here: calendar by `session_at`

The calendar is a query over sessions that already have a date. `GET /calendar?from=&to=&plan_id=` returns the current user’s sessions whose `session_at` falls in the range. Unscheduled sessions (`session_at` null) are omitted. There are no generated weekday slots and no rows that exist only on the calendar.

Optional `plan_id` uses the same rule as the session list: another user’s plan yields an empty list, not 404. A reversed range is **400** `from must not be after to`. Sort the payload by **`session_at` ascending** (the session list stays `created_at` descending; the calendar is a different order).

Each item is a small DTO: `id`, `name`, `session_at`, `status`, `plan_id`. The full exercise tree stays on `GET /sessions/{id}`.

**Docs & tutorials:**

- [FastAPI — query parameters](https://fastapi.tiangolo.com/tutorial/query-params/) — `from`, `to`, and optional `plan_id`
- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/) — a calendar item that is thinner than `SessionRead`
- S3-06 — reuse the date-range and plan filter instead of a second query language

### Your task

Add an owner-scoped calendar list for dated sessions. Your deliverable is `GET /calendar` returning only the caller’s sessions in range, sorted by `session_at`.

### Instructions

1. Add `backend/app/schemas/calendar.py` with the five fields above. `session_at` is required on this DTO because unscheduled rows are excluded.
2. Add `backend/app/services/calendar.py` that calls the session list (or repository) with the caller’s `user_id`, the range, `unscheduled=false`, and the optional `plan_id`, then sorts by `session_at` ascending.
3. Add `GET /calendar` in `backend/app/api/calendar.py`. Alias the query names `from` and `to` the same way as S3-06. Register the router.
4. Check your work: a dated session inside the window appears; one outside does not; an unscheduled session does not; another user’s dated session does not. `plan_id` for the caller’s plan narrows the list. A foreign `plan_id` returns `[]`. `from` after `to` returns 400 `from must not be after to`. Two sessions on different days come back in date order.

### Stay in scope

- Leave month and week grids for S3-19.
- Leave clone for S3-07. The calendar UI will call clone; this ticket only lists.
- Leave Google Calendar sync out.

### Hints

- Implement the range check once if sessions and calendar both need it, so the 400 detail stays identical.
- The service may wrap `list_sessions`. Override the sort for this response so the grid is chronological.

### Acceptance criteria

- [ ] `GET /calendar` returns only the current user’s sessions with `session_at` in range
- [ ] Results are ordered by `session_at` ascending
- [ ] Optional `plan_id` filters; a foreign plan id returns an empty list
- [ ] Unscheduled sessions are absent
- [ ] A reversed range is 400 `from must not be after to`
- [ ] Missing JWT is 401

### Suggested paths

`backend/app/api/calendar.py`, `backend/app/services/calendar.py`, `backend/app/schemas/calendar.py`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-12` in the message, for example `S3-12: short summary`. Never commit `.env` or secrets.

---

## S3-13 — TanStack Query setup

| Field          | Value                  |
| -------------- | ---------------------- |
| **Type**       | feature                |
| **Week**       | 2                      |
| **Priority**   | Must                   |
| **Estimate**   | S                      |
| **Depends on** | Sprint 2 auth client   |

### New here: TanStack Query

Sprint 2 stored the JWT and called the API with `fetch`. Sprint 3 screens share the same lists (sessions, plans, calendar). **TanStack Query** caches those responses, refetches when a key changes, and gives you `isLoading` / `isError` instead of a hand-rolled `useEffect`.

A **query key** names the cache entry. The same screen with different filters needs different keys, or Monday’s calendar will show last month’s data. Put the keys in one module so mutations can invalidate a prefix (`['sessions']`) and every filtered list refreshes.

The API client should keep sending `Authorization: Bearer <token>` from the Sprint 2 `localStorage` token. A **401** (other than login) clears that token so the protected layout can send the user back to login.

**Docs & tutorials:**

- [TanStack Query — overview](https://tanstack.com/query/latest/docs/framework/react/overview) — `QueryClient` and `useQuery`
- [Query keys](https://tanstack.com/query/latest/docs/framework/react/guides/query-keys) — include every filter in the key
- [Invalidation from mutations](https://tanstack.com/query/latest/docs/framework/react/guides/invalidations-from-mutations) — refresh lists after create, clone, and delete

### Your task

Install TanStack Query, wrap the app in `QueryClientProvider`, and define the key helpers later pages will import. Your deliverable is the provider, a key module, and a client that attaches the bearer token. At least one existing call (health or `/auth/me` is enough) should go through `useQuery` so you know the provider works.

### Instructions

1. Add `@tanstack/react-query`. Create `frontend/src/api/queryClient.ts` with a `QueryClient` (a small retry count, such as 1, is enough).
2. In `frontend/src/main.tsx`, wrap the tree with `QueryClientProvider` outside `BrowserRouter`.
3. Add `frontend/src/api/queryKeys.ts` with helpers:
   - `sessions(filters)` → `['sessions', filters]`
   - `session(id)` → a detail key
   - `plans` and `plan(id)`
   - `calendar(from, to, planId)`
   - `activityTypes`
   - `goals(active)`
4. Give session filters a typed shape: `from`, `to`, `status`, `activityTypeId`, `unscheduled`, `planId`, and later `page` / `limit` (S3-S1 may be the first caller of page and limit).
5. Point `frontend/src/api/client.ts` at `VITE_API_BASE_URL` (default `http://localhost:8000`). Attach the bearer token from the Sprint 2 token helper. On 401, clear the token except for the login request itself. Throw an error that includes the HTTP status and the API `detail` message so pages can show it.
6. Check your work: the app still loads, React Query devtools or a temporary `useQuery` shows a successful request, and a call without a token does not attach `Authorization`.

### Stay in scope

- Leave the sessions page, designer, plans, and calendar pages for S3-14 onward. This ticket is the client, the provider, and the keys.
- Leave server state in `useState` + `useEffect` behind. New Sprint 3 reads go through `useQuery`.

### Hints

- Invalidate `['sessions']` after a session mutation and `['calendar']` when a date or clone changes. A key prefix match refreshes every filter variant.
- Keep the token read in the client, not inside every page.

### Acceptance criteria

- [ ] `QueryClientProvider` wraps the app
- [ ] Query key helpers exist for sessions, plans, calendar, activity types, and goals
- [ ] The API client sends the bearer token and clears it on 401
- [ ] At least one `useQuery` runs successfully while logged in

### Suggested paths

`frontend/src/api/queryClient.ts`, `frontend/src/api/queryKeys.ts`, `frontend/src/api/client.ts`, `frontend/src/main.tsx`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-13` in the message, for example `S3-13: short summary`. Never commit `.env` or secrets.

---

## S3-14 — Sessions list and filters UI

| Field          | Value         |
| -------------- | ------------- |
| **Type**       | feature       |
| **Week**       | 2             |
| **Priority**   | Must          |
| **Estimate**   | L             |
| **Depends on** | S3-06, S3-13  |

### New here: a filtered list on the protected route

The sessions page is the logbook index. It calls `GET /sessions` with the S3-06 query parameters and shows only what the API returns — the layout is already behind the Sprint 2 protected route, and the API is scoped to the token, so this page does not filter by user id in the browser.

Show each row’s name, date or the word **Unscheduled** when `session_at` is null, status, and a short exercise summary (activity names from the nested items). Link each row to the designer (`/sessions/:id`).

Keep filter controls in local state and send them when the user applies. Changing a dropdown should not fire a request on every keystroke unless you prefer that; an Apply action is enough and matches a clear “these filters are active” moment.

**Docs & tutorials:**

- [TanStack Query — `useQuery`](https://tanstack.com/query/latest/docs/framework/react/guides/queries) — the query key includes the applied filters
- [React Router — `Link`](https://reactrouter.com/en/main/components/link) — row opens the designer
- S3-06 — parameter names the client must send: `from`, `to`, `status`, `activity_type_id`, `unscheduled`, `plan_id`

### Your task

Build the protected sessions list with working filters. Your deliverable is a page that loads the caller’s sessions, applies the API filters, and links through to edit.

### Instructions

1. Add the route `/sessions` inside the protected layout, and a nav link in the header.
2. Add `listSessions` on the API client. Map UI filters to the query string. Send datetimes for `from` / `to` (start of the from-day, end of the to-day) so a single calendar day still matches.
3. `useQuery` with `queryKeys.sessions(appliedFilters)`. Also load plans and activity types so the plan and activity dropdowns have labels (`queryKeys.plans`, `queryKeys.activityTypes`).
4. Controls: from date, to date, status (`planned`, `in_progress`, `completed`), schedule (all / dated / unscheduled), plan, and activity. When the schedule is “unscheduled,” disable the date inputs and omit `from` / `to`. If from is after to, show a validation message and skip the request.
5. Provide Apply and Clear. Clear resets the draft and the applied filters.
6. Empty copy when there are no rows (a first-session prompt when no filters are on; a “nothing matches” line when filters are on). Wire the real empty component in S3-21 if you want to share it; a plain message is enough here.
7. Check your work logged in: the list matches OpenAPI for the same filters, Unscheduled rows show that label, and logging in as another user shows a different list (or an empty one).

### Stay in scope

- Leave create/edit/clone forms for S3-15 and S3-16. A link to `/sessions/new` may be a dead route until then, or you can add the route in S3-15.
- Leave page size and previous/next for S3-S1.
- Leave the activity `<select>` polish for S3-17. A basic `<select>` of activity names is enough on this page until that component exists; switch to it when S3-17 lands.

### Hints

- Store `draft` and `applied` separately so typing a date does not refetch until Apply.
- `exerciseSummary` can join item activity names. The list payload from S3-04 already includes items.

### Acceptance criteria

- [ ] `/sessions` loads only the logged-in user’s sessions
- [ ] Date, status, unscheduled, plan, and activity filters are sent to the API
- [ ] Each row shows name, date or Unscheduled, status, and an exercise summary, and links to the session
- [ ] A reversed from/to range is blocked in the form
- [ ] Another account does not see these rows

### Suggested paths

`frontend/src/pages/SessionsPage.tsx`, `frontend/src/api/client.ts`, `frontend/src/sessions/display.ts`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-14` in the message, for example `S3-14: short summary`. Never commit `.env` or secrets.

---

## S3-15 — Session designer (planned and actual)

| Field          | Value                  |
| -------------- | ---------------------- |
| **Type**       | feature                |
| **Week**       | 2                      |
| **Priority**   | Must                   |
| **Estimate**   | L                      |
| **Depends on** | S3-05, S3-09, S3-13    |

### New here: the session designer

The designer is the form behind `/sessions/new` and `/sessions/:sessionId`. It edits one session: metadata, an ordered list of exercises, and a planned/actual pair for every unit the exercise allows.

Build the inputs from **unit links** (`GET /activity-types`), not from a `unit_hint`. For a unit with `per_set` false, show one Planned and one Actual field. For `per_set` true, show Set 1, Set 2, … with Planned and Actual on each, plus Add set / Remove set. Empty planned and empty actual means “omit this measurement on save” (the API rejects a measurement where both are null). `session_at` may be cleared so the session stays unscheduled.

**Docs & tutorials:**

- [TanStack Query — mutations](https://tanstack.com/query/latest/docs/framework/react/guides/mutations) — `useMutation` for create and update
- [React — controlled inputs](https://react.dev/reference/react-dom/components/input) — planned and actual fields
- S3-05 — the JSON the form must produce (`planned_value`, `actual_value`, `set_index`)

### Your task

Ship a form that creates and saves a multi-exercise session with planned and actual values. Your deliverable is the designer page, a measurement editor, and a draft mapper that turns the form into the S3-04/S3-05 body.

### Instructions

1. Routes: `/sessions/new` and `/sessions/:sessionId` inside the protected layout. On edit, `useQuery` `GET /sessions/{id}`. A 404 shows a plain “Session not found.” message.
2. Add `frontend/src/sessions/draft.ts` with an empty draft, a function that fills the draft from a session, and `toSessionWrite` that emits the API body. Drop measurements where both values are blank.
3. Fields: name, `datetime-local` for `session_at` (empty → null), status, optional plan select (the caller’s plans), intensity 1–10 or empty, notes.
4. Exercises: add from the activity list (S3-17’s selector, or a `<select>` until that ticket), reorder up/down, remove, notes per exercise. Changing the activity rebuilds measurement rows from that activity’s unit links.
5. Add `frontend/src/components/MeasurementEditor.tsx`. One row of Planned and Actual per non-set unit. Set blocks for `per_set` units, with `set_index` 0, 1, 2… in the payload.
6. Save calls `POST /sessions` or `PATCH /sessions/{id}`. After create, navigate to `/sessions/:id`. After update, stay on the page and show a saved confirmation. Invalidate `['sessions']` and `['calendar']`.
7. Check your work: save Bench press with two sets of planned reps and weight and empty actuals; reload and see the same sets. Clear the date and confirm `session_at` is null. A Running session shows duration and distance once each, not as sets.

### Stay in scope

- Leave delete and clone controls for S3-16. You can leave a gap in the page for them.
- Leave plan create UI for S3-18. Selecting an existing `plan_id` is in scope.
- Client-side checks complement the API. The server still rejects a bad unit or a missing `set_index`.

### Hints

- Keep the draft in `useState`. React Query holds the server session; the draft is what the user is editing.
- `datetime-local` has no timezone. Convert to an ISO string on save and back to local input on load.

### Acceptance criteria

- [ ] Create and update save a multi-exercise session
- [ ] A strength exercise can store per-set planned and actual values
- [ ] A session-level exercise stores one pair per linked unit
- [ ] `session_at` may be empty
- [ ] Optional `plan_id` is sent only when a plan is selected
- [ ] A missing session id shows “Session not found.”

### Suggested paths

`frontend/src/pages/SessionFormPage.tsx`, `frontend/src/components/MeasurementEditor.tsx`, `frontend/src/sessions/draft.ts`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-15` in the message, for example `S3-15: short summary`. Never commit `.env` or secrets.

---

## S3-16 — Edit, delete, and clone session UI

| Field          | Value         |
| -------------- | ------------- |
| **Type**       | feature       |
| **Week**       | 2             |
| **Priority**   | Must          |
| **Estimate**   | M             |
| **Depends on** | S3-07, S3-15  |

### New here: clone from the designer

Edit is the S3-15 form loaded from `GET`. This ticket adds **delete** (with a confirm step) and **clone** (calls `POST /sessions/{id}/clone`).

Clone fields: a copy name (default the current name) and a copy date. An empty date means unscheduled (`session_at` omitted or null). The API then keeps planned values, clears actuals, sets status to `planned`, and leaves `plan_id` empty unless you send one — this form does **not** send `plan_id`, so the copy is off the plan. Say that in the UI so the demo is obvious.

After a successful clone, go to the new session. After delete, go back to `/sessions`. Invalidate session and calendar queries. Show the API message on failure. A 404 on clone or save is “Session not found.” (or the response detail).

**Docs & tutorials:**

- [TanStack Query — invalidation](https://tanstack.com/query/latest/docs/framework/react/guides/invalidations-from-mutations) — lists and the open detail go stale after clone and delete
- [React Router — `useNavigate`](https://reactrouter.com/en/main/hooks/use-navigate) — open the new session after clone
- S3-07 — body is `name` and `session_at` only from this form

### Your task

Add delete and clone to the session designer, and make the snapshot visible. Your deliverable is a confirmed delete, a clone action, and a check that editing the source leaves the clone alone.

### Instructions

1. On an existing session, add a clone card: copy name, copy date (`datetime-local`, optional), and a Clone button. Call `cloneSession(id, { name, session_at })`. Navigate to the new id. A short banner on the new page can say it was cloned (planned kept, actuals cleared, plan not copied).
2. Add delete with an explicit confirm (a second click or a confirm control). `DELETE` returns 204; then navigate to `/sessions`.
3. On mutation errors, show the message from the API client. Map 404 to a not-found line. The API uses 404 for foreign ids; you do not need a separate 403 path for the happy demo, but if a 403 ever arrives, show a “you cannot change this session” line.
4. Invalidate `['sessions']` and `['calendar']` on success.
5. Check your work: clone a session that has actuals, open the copy, confirm actuals are empty and planned values remain, edit the source (add an exercise), reload the copy, and confirm the copy did not gain that exercise.

### Stay in scope

- Leave the calendar’s clone-onto-a-date panel for S3-19. Both call the same endpoint.
- Leave bulk delete and undo out.

### Hints

- Disable the clone and delete buttons while the mutation is pending so a double click does not create two copies.
- The new session’s `source_session_id` is on the GET payload if you want to show “Copied from …” later. The banner text is enough for the demo.

### Acceptance criteria

- [ ] Edit still saves through the S3-15 form
- [ ] Delete asks for confirmation, then removes the session and returns to the list
- [ ] Clone from the UI keeps planned values and clears actuals
- [ ] The clone is unscheduled when the date is left empty, and it is not attached to the source plan
- [ ] Editing the source does not change the clone
- [ ] A 404 shows a clear not-found message

### Suggested paths

`frontend/src/pages/SessionFormPage.tsx`, `frontend/src/api/client.ts`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-16` in the message, for example `S3-16: short summary`. Never commit `.env` or secrets.

---

## S3-17 — Activity type selector

| Field          | Value         |
| -------------- | ------------- |
| **Type**       | feature       |
| **Week**       | 2             |
| **Priority**   | Must          |
| **Estimate**   | M             |
| **Depends on** | S3-09, S3-13  |

### New here: picking an exercise from the catalog

The designer and the session filters both need the same control: a list of exercises from `GET /activity-types`, grouped into system exercises and the caller’s custom ones, with the unit links visible in the label. The option text is the exercise name plus a short unit summary built from `unit_links` (for example “Bench press — reps, weight” or “Running — duration, distance”). That summary replaces any `unit_hint` string. There is no hint column.

**Docs & tutorials:**

- [MDN — `<optgroup>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/optgroup) — “Exercises” vs “Your exercises”
- S3-09 — `is_system`, `name`, and `unit_links[].per_set` / unit name
- S3-15 — the designer calls `onChange` with the selected activity id and rebuilds measurements

### Your task

Add a shared activity selector and use it in the session designer. Your deliverable is one component that lists system and custom exercises with their units.

### Instructions

1. Add `frontend/src/components/ActivityTypeSelect.tsx`. Props: the activity list, the current id, `onChange`, and an optional empty option (`allowEmpty`, `emptyLabel`) for filters.
2. Render a `<select>` with two groups: system (`is_system`) and the caller’s exercises. Option label = name + unit summary from `unit_links` in `sort_order`.
3. Under the control, show the selected exercise’s units in a line of helper text. If the current id is not in the list, show “Unknown exercise” so a stale id is visible.
4. Use the component when adding or changing an exercise in `SessionFormPage`. On change, rebuild that item’s measurements from the new activity’s links (S3-15 draft helper).
5. Use it on the sessions filter (S3-14) with `allowEmpty` so “any activity” is possible.
6. Check your work: Bench press shows a per-set unit summary; Running shows duration and distance; a custom exercise from S3-09 appears under “Your exercises” only for the user who created it.

### Stay in scope

- Leave creating a custom exercise in this dropdown for later. POST stays available in OpenAPI; this control only lists.
- Leave goals’ exercise picker for S3-23. You can reuse this component there.

### Hints

- Pass activities in from the parent’s `useQuery`. The selector stays presentational and easy to reuse.
- Unit summary should mention `per_set` only if it helps the label; the measurement editor already branches on that flag.

### Acceptance criteria

- [ ] The designer uses `ActivityTypeSelect` to add and change exercises
- [ ] System and custom exercises are grouped
- [ ] Labels reflect API unit links, with no `unit_hint`
- [ ] The sessions filter can use the same component with an empty option

### Suggested paths

`frontend/src/components/ActivityTypeSelect.tsx`, `frontend/src/pages/SessionFormPage.tsx`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-17` in the message, for example `S3-17: short summary`. Never commit `.env` or secrets.

---

## S3-18 — Plans UI

| Field          | Value         |
| -------------- | ------------- |
| **Type**       | feature       |
| **Week**       | 3             |
| **Priority**   | Must          |
| **Estimate**   | L             |
| **Depends on** | S3-08, S3-13  |

### New here: a plan is a named list of sessions

The plans UI lists programs, opens one, and attaches sessions the caller already owns. Order on the detail page follows the API: **`session_at` ascending, nulls last**. Show dated members first and unscheduled members in their own section so the nulls are visible. There is no drag-and-drop reorder and no weekday grid. `start_date` and `length_weeks` are editable metadata.

Attach calls `POST /plans/{id}/sessions/{sessionId}`. Detach calls the matching DELETE. The attach dropdown lists the caller’s sessions that are not already on this plan. Label a session that already has another `plan_id` so it is clear the attach will move it.

**Docs & tutorials:**

- [TanStack Query — dependent queries](https://tanstack.com/query/latest/docs/framework/react/guides/dependent-queries) — plan detail and the session list for the dropdown
- [TanStack Query — invalidation](https://tanstack.com/query/latest/docs/framework/react/guides/invalidations-from-mutations) — refresh plans, sessions, and calendar after attach
- S3-08 — detail payload `sessions[]` is already ordered

### Your task

Build list, create, edit, delete, attach, and detach for plans. Your deliverable is `/plans` and `/plans/:planId`, using only the caller’s sessions.

### Instructions

1. Add routes and a header link. `PlansPage` loads `GET /plans` and offers a create form: name (required), start date, length in weeks (integer ≥ 1), notes. On success, navigate to `/plans/:id`.
2. `PlanDetailPage` loads `GET /plans/{id}`. A 404 renders “Plan not found.” Edit the same fields with PATCH. Delete asks for confirmation, then returns to `/plans`. Tell the user that sessions stay in the log and leave the plan.
3. Split members into dated and unscheduled sections, in the order the API returned. Each row links to the session designer and has Detach.
4. Load the caller’s sessions for the attach `<select>`. Submitting calls the attach route. Invalidate plan, session, and calendar keys.
5. If attach returns 404 `Session not found`, show that message (the session is missing or not theirs).
6. Check your work: attach an earlier session, a later one, and an unscheduled one; confirm the sections follow `session_at`. Log in as someone else and confirm their plan URL 404s and their sessions are not in the dropdown.

### Stay in scope

- Leave calendar placement for S3-19. Attaching does not set `session_at`.
- Leave a junction editor, sequence numbers, and weekday columns out.
- Leave creating a brand-new session inside the plan page out. Create sessions in the designer, then attach them here.

### Hints

- The dropdown can say “(unscheduled)” and “(moves from another plan)” so the `plan_id` rule is visible.
- `length_weeks` is a number field. Empty means null, not zero.

### Acceptance criteria

- [ ] The owner can list, create, edit, and delete a plan
- [ ] Attach and detach change membership through the API
- [ ] Dated members appear in `session_at` order, then unscheduled members
- [ ] `start_date` and `length_weeks` display and save as metadata
- [ ] Another user’s plan id shows “Plan not found.” and their sessions cannot be attached

### Suggested paths

`frontend/src/pages/PlansPage.tsx`, `frontend/src/pages/PlanDetailPage.tsx`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-18` in the message, for example `S3-18: short summary`. Never commit `.env` or secrets.

---

## S3-19 — Calendar UI

| Field          | Value               |
| -------------- | ------------------- |
| **Type**       | feature             |
| **Week**       | 3                   |
| **Priority**   | Must                |
| **Estimate**   | L                   |
| **Depends on** | S3-12, S3-07, S3-13 |

### New here: month and week over dated sessions

The calendar reads `GET /calendar`. It does not invent workouts for empty days. **Month** and **week** are two views of the same list: you change the visible `from` / `to` and render the sessions whose `session_at` falls on each day.

A small date helper is enough (`frontend/src/calendar/range.ts`). You do not need a third-party calendar package or Google sync. Use a Monday-first week. The month grid can be six weeks (42 days) with days outside the current month dimmed. The week view is seven days.

From a session chip, **clone onto a date** calls S3-07 with a required date. That is the calendar’s “do this workout on Monday” action. The designer clone (S3-16) may leave the date empty; this one always sends `session_at` on the chosen day. Keep the time of day from the original session when you build that timestamp, so a 18:00 session stays at 18:00.

Optional plan filter: “All plans” or one plan id, passed as `plan_id`. Color or label chips by `status`.

**Docs & tutorials:**

- [TanStack Query — query keys](https://tanstack.com/query/latest/docs/framework/react/guides/query-keys) — key by `from`, `to`, and `planId`
- [MDN — `Date`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date) — month grids and ISO ranges
- S3-12 — the payload is `id`, `name`, `session_at`, `status`, `plan_id`

### Your task

Build month and week calendar views for the current user’s dated sessions, with a plan filter and clone-onto-a-date. Your deliverable is `/calendar` backed only by `GET /calendar` and `POST /sessions/{id}/clone`.

### Instructions

1. Add the route and a header link. State: view (`month` \| `week`), a cursor date, and an optional `plan_id`.
2. Compute the visible days and the `from` / `to` instants for that range. `useQuery` with `queryKeys.calendar(from, to, planId)`.
3. Render weekday headers and a day grid. Put each session on the day of its `session_at`. The name links to `/sessions/:id`. Mark today. Previous, Today, and Next move the cursor. Toggle Month and Week.
4. Plan `<select>` from `GET /plans`, including All plans.
5. Clone opens a small panel on that chip: copy name, a required date input, and confirm. Call clone with `session_at` on that date. On success, move the cursor to the new date, invalidate calendar and session queries, and offer a link to the new session. An empty date shows “Choose a date.”
6. Empty state when the range has no sessions (mention the plan filter when one is selected).
7. Check your work: a dated session appears in month and week; an unscheduled session does not; changing the plan filter hides other plans; clone onto next Monday creates a new session that shows on that day; the source session is still on its original day.

### Stay in scope

- Leave drag-and-drop rescheduling out. Clone is how a session lands on another day.
- Leave Google Calendar, invites, and recurrence out.
- Leave unscheduled sessions off this grid. They remain on the sessions list.

### Hints

- Query only the visible range so month and week stay cheap.
- Status can be a CSS class or a badge (`planned`, `in_progress`, `completed`). Any consistent distinction is fine.

### Acceptance criteria

- [ ] Month and week views both render `GET /calendar` for the visible range
- [ ] Only the current user’s dated sessions appear
- [ ] The plan filter is sent as `plan_id`
- [ ] Clone onto a chosen date creates a new session via S3-07 and shows it on that day
- [ ] The source session remains on its original date after clone

### Suggested paths

`frontend/src/pages/CalendarPage.tsx`, `frontend/src/calendar/range.ts`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-19` in the message, for example `S3-19: short summary`. Never commit `.env` or secrets.

---

## S3-20 — Dashboard recent sessions

| Field          | Value         |
| -------------- | ------------- |
| **Type**       | feature       |
| **Week**       | 3             |
| **Priority**   | Must          |
| **Estimate**   | M             |
| **Depends on** | S3-04, S3-13  |

### New here: the home page as a recent log

The protected home route (`/`) is the dashboard. It shows a short list of the **current user’s dated sessions**, newest `session_at` first, with a link to edit each one. Cap the list (eight is a good default) so the page stays a summary. Unscheduled sessions stay off this list; they live on `/sessions`.

When there are no dated sessions, show an empty state that links to `/sessions/new` (“Create your first session”). You can share that empty component with S3-21.

**Docs & tutorials:**

- [TanStack Query — `useQuery`](https://tanstack.com/query/latest/docs/framework/react/guides/queries) — `queryKeys.sessions({ unscheduled: false })`
- S3-06 — `unscheduled=false` returns only dated rows
- S3-14 — reuse the date label, status badge, and exercise summary helpers

### Your task

Replace the placeholder home content with recent dated sessions for the logged-in user. Your deliverable is a dashboard that cannot show another account’s rows and that explains itself when the list is empty.

### Instructions

1. On `frontend/src/pages/DashboardPage.tsx`, query sessions with `unscheduled: false`. Sort the result by `session_at` descending and keep the first eight.
2. Each card shows name, formatted `session_at`, status, and an exercise summary, and links to `/sessions/:id`.
3. Empty state with a link to create a session. Error state when the query fails (S3-21’s banner if it already exists).
4. Keep any existing health indicator if Sprint 1 left one on the dashboard; it can sit beside the list.
5. Check your work: create two dated sessions and one unscheduled session. The dashboard shows the dated ones, newest first, and omits the unscheduled one. A second user sees their own list (or the empty state), not yours.

### Stay in scope

- Leave charts, streaks, and goal progress for Sprint 4.
- Leave the full filterable list on `/sessions`. The dashboard is a preview.
- The cap can be applied in the browser. Server pagination is S3-S1.

### Hints

- Reuse `formatSessionAt` and `exerciseSummary` from the sessions display helpers so the two pages match.
- The query key must include `unscheduled: false`, or it will collide with an unfiltered sessions cache entry.

### Acceptance criteria

- [ ] The dashboard lists only the logged-in user’s dated sessions
- [ ] Order is `session_at` descending, capped to a short recent set
- [ ] Each row links to the session editor
- [ ] An empty log shows a create-session empty state

### Suggested paths

`frontend/src/pages/DashboardPage.tsx`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-20` in the message, for example `S3-20: short summary`. Never commit `.env` or secrets.

---

## S3-21 — Empty and error states

| Field          | Value                  |
| -------------- | ---------------------- |
| **Type**       | feature                |
| **Week**       | 3                      |
| **Priority**   | Should                 |
| **Estimate**   | S                      |
| **Depends on** | S3-14, S3-18, S3-19    |

### New here: shared empty and error UI

A failed save or an empty list should be visible. Silent `catch` blocks make the demo look frozen. Two small components cover the sprint:

- **EmptyState** — short title, optional explanation, optional action link (“Create your first session”)
- **ErrorBanner** — the API or network message, visible above the form or list

Use them on the sessions list, plan list and detail, calendar, and dashboard. A 404 on a detail page can stay a quiet “Session not found.” / “Plan not found.” line; that is the ownership message from S3-11, not a generic crash. Save and clone failures use the banner.

**Docs & tutorials:**

- [TanStack Query — query status](https://tanstack.com/query/latest/docs/framework/react/guides/queries) — `isPending`, `isError`, `error`
- [React — conditional rendering](https://react.dev/learn/conditional-rendering) — empty vs loaded vs failed
- S3-13 — the client error already carries `status` and `message`

### Your task

Add shared empty and error components and use them on sessions, plans, and calendar so a failure is visible. Your deliverable is `EmptyState` and `ErrorBanner` wired into those pages.

### Instructions

1. Add `frontend/src/components/StatusMessage.tsx` (or equivalent) exporting `EmptyState` and `ErrorBanner`.
2. Sessions list: empty state for no rows (different copy when filters are active versus a brand-new log) and a banner when `useQuery` fails.
3. Plans list and plan detail: empty state when the user has no plans; banner when create, update, attach, or delete fails.
4. Calendar: empty state when the visible range has no sessions; banner when the calendar query fails. Mention the active plan filter in the empty copy when one is set.
5. Dashboard: reuse the empty state from S3-20 if it is still a one-off.
6. Check your work: stop the API and confirm each page shows a banner instead of an endless spinner. With the API up and no data, confirm the empty copy and the create link.

### Stay in scope

- Leave a global toast system and retry widgets out. A banner and an empty panel are enough.
- Leave Sprint 4 chart empty states out.
- This is a Should. Skip it only if the demo pages already show the same copy clearly — then this ticket is the extraction into shared components.

### Hints

- One `failureMessage(error)` helper can turn the client error into a string so pages do not parse JSON themselves.
- Keep 404 detail pages as a not-found sentence. Reserve the banner for actions the user just attempted and for list queries that failed.

### Acceptance criteria

- [ ] Sessions, plans, and calendar show an empty state when the list is empty
- [ ] Failed loads and failed saves show an error banner
- [ ] A 404 on a session or plan detail still reads as not found
- [ ] The empty log offers a way to create a session

### Suggested paths

`frontend/src/components/StatusMessage.tsx`, `frontend/src/pages/SessionsPage.tsx`, `frontend/src/pages/PlansPage.tsx`, `frontend/src/pages/CalendarPage.tsx`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-21` in the message, for example `S3-21: short summary`. Never commit `.env` or secrets.

---

## S3-22 — IDOR demo documentation

| Field          | Value   |
| -------------- | ------- |
| **Type**       | docs    |
| **Week**       | 3       |
| **Priority**   | Must    |
| **Estimate**   | S       |
| **Depends on** | S3-11   |

### New here: a demo another student can repeat

S3-11 fixed the behavior. This ticket writes it down so a classmate can reproduce it without reading the services. The convention to document is the one the API implements:

| Call | Result |
| ---- | ------ |
| No token | **401** |
| GET, PATCH, DELETE, or clone of another user’s session | **404** `Session not found` |
| GET, PATCH, DELETE of another user’s plan, or attach using their plan | **404** `Plan not found` |
| GET, PATCH, DELETE of another user’s goal | **404** `Goal not found` |
| Attach their session onto your plan | **404** `Session not found` |
| `GET /sessions` or `GET /calendar` with their `plan_id` | **200** and an empty list |
| A random UUID | the same 404 detail as a real foreign id |

Lists never include the other user’s rows. Say explicitly that object fetches use **404**, not 403, and that the detail matches a missing id.

**Docs & tutorials:**

- [OWASP — IDOR](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References) — what the demo is proving
- [curl](https://curl.se/docs/manpage.html) — send `Authorization: Bearer` as user B
- S3-11 — the status and detail strings to expect

### Your task

Write a short classmate-facing script at `docs/idor-demo.md`. Your deliverable is steps that create two users, have B call A’s ids, and record the expected responses.

### Instructions

1. Open with the status table above and one sentence on why 404 is used for both missing and foreign ids.
2. “Before you start”: how you run the stack (Compose, migrate, seed) so the catalog units exist for a goal.
3. Register and log in user A and user B. Show a small snippet that stores each access token (PowerShell or curl is fine).
4. As A, create a session, a plan, and a goal. GET each id as A and show success.
5. As B, GET, PATCH, and DELETE A’s session, plan, and goal; clone A’s session; attach A’s session to B’s plan. Show the expected JSON detail for each 404. Repeat one call with a random UUID and show the same detail.
6. As B, `GET /sessions`, `GET /plans`, `GET /goals`, and `GET /calendar`. They are empty (or contain only B’s rows). `GET /sessions?plan_id=` and `GET /calendar?plan_id=` with A’s plan id return 200 and `[]`.
7. As A, GET the original session again and show that B’s attempts did not change it.
8. Check your work: hand the file to a classmate (or follow it yourself in a clean shell) and confirm every status matches.

### Stay in scope

- Leave automated tests for S3-S2. This file is a manual script.
- Leave a full threat model and Sprint 6 hardening out.
- Document the API. A screenshot of the UI “not found” line is optional.

### Hints

- Use `curl.exe` on Windows if `curl` is an alias for `Invoke-WebRequest`.
- Create the goal only after `GET /activity-types` so you have a real `unit_type_id`.

### Acceptance criteria

- [ ] `docs/idor-demo.md` can be followed from a clean login without reading the source
- [ ] The 404 details for session, plan, and goal are stated
- [ ] The script covers clone, attach, list, and calendar
- [ ] It states that a foreign `plan_id` filter returns an empty 200, and that object ids return 404 rather than 403

### Suggested paths

`docs/idor-demo.md`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-22` in the message, for example `S3-22: short summary`. Never commit `.env` or secrets.

---

## S3-23 — Optional Goals UI

| Field          | Value         |
| -------------- | ------------- |
| **Type**       | feature       |
| **Week**       | 3             |
| **Priority**   | Stretch       |
| **Estimate**   | M             |
| **Depends on** | S3-10, S3-13  |

### New here: period goals on a page

This page manages **period goals** (a weekly or monthly target for a unit). It is not the planned-set editor. Label the screen “Period goals” in the header so it stays distinct from session measurements.

The API already supports full CRUD. The page can stay small: create, list, filter by active, and activate or deactivate. Edit-every-field and delete can wait.

**Docs & tutorials:**

- [TanStack Query — mutations](https://tanstack.com/query/latest/docs/framework/react/guides/mutations) — create and toggle `active`
- S3-10 — `unit_type_id`, optional `activity_type_id`, `target_value` > 0, `period`, `active`
- S3-09 — unit choices come from the activity catalog’s unit links, not a free-text unit

### Your task

Add a simple period-goals page for the logged-in user. Your deliverable is `/goals` that creates and lists goals and can mark one inactive or active again.

### Instructions

1. Add the route and a “Period goals” nav link inside the protected layout.
2. Load activity types once and build the unit dropdown from their unit links (unique units). Optional exercise dropdown uses the same activity list, with an empty “any exercise” value.
3. Create form: unit (required), period (`week` or `month`), target (number > 0), optional exercise. POST `/goals`. Show a validation message before sending an empty target.
4. List `GET /goals` with a Show filter: all, active, inactive (`active` query param). Each row shows the target, unit, period, optional exercise name, and an Active/Inactive badge. A button sends PATCH `{ active: false }` or `{ active: true }`.
5. Invalidate `queryKeys.goals(...)`. A 404 on a stale id shows the API detail.
6. Check your work: create “20 km / week,” see it in the list, deactivate it, and confirm the inactive filter still finds it. A second user does not see it.

### Stay in scope

- Leave charts of actual vs target for Sprint 4.
- Leave this off the Must demo path. The API from S3-10 is the required piece.
- Call them period goals in the UI copy. Planned reps stay on the session designer.

### Hints

- Deactivate is a PATCH of `active`. You do not need a delete button for the stretch demo.
- If a unit appears on several exercises, show it once in the unit dropdown.

### Acceptance criteria

- [ ] The owner can create a period goal and see it in the list
- [ ] The list can filter by active / inactive
- [ ] Activate and deactivate call PATCH
- [ ] The page is labeled as period goals
- [ ] Another user’s goals are not listed

### Suggested paths

`frontend/src/pages/GoalsPage.tsx`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-23` in the message, for example `S3-23: short summary`. Never commit `.env` or secrets.

---

## S3-S1 — Pagination

| Field          | Value   |
| -------------- | ------- |
| **Type**       | feature |
| **Week**       | —       |
| **Priority**   | Stretch |
| **Estimate**   | S       |
| **Depends on** | S3-06, S3-14 |

### New here: paging the session list

`GET /sessions` from S3-06 returns every matching row. A long log needs a page. Add **offset pagination** with `page` and `limit` on that route only. Calendar and plans can stay unpaged.

| Query | Meaning |
| ----- | ------- |
| `page` | 1-based, default 1, minimum 1 |
| `limit` | Optional page size, 1–100. When omitted, return every matching row and force `page` to 1 in the response |

Response shape:

```json
{ "items": [], "total": 0, "page": 1, "limit": null }
```

`total` is the count **before** slicing, still scoped to the current user and the other filters. `limit` is null when the client asked for the full list. Order stays `created_at` descending, then slice.

**Docs & tutorials:**

- [FastAPI — query parameters](https://fastapi.tiangolo.com/tutorial/query-params/) — `page` and `limit` with bounds
- [SQLAlchemy — LIMIT / OFFSET](https://docs.sqlalchemy.org/en/20/core/selectable.html#sqlalchemy.sql.expression.Select.limit) — `limit` and `offset` after the filter
- [TanStack Query — keys](https://tanstack.com/query/latest/docs/framework/react/guides/query-keys) — include `page` and `limit` in `queryKeys.sessions`

### Your task

Page the session list in the API and on `/sessions`. Your deliverable is `page` and `limit` documented in OpenAPI, a `{ items, total, page, limit }` body, and previous/next controls on the sessions page.

### Instructions

1. Change `GET /sessions` so the success model is a page object. Keep the S3-06 filters. Apply them first, count `total`, then apply offset `(page - 1) * limit` when `limit` is set.
2. Reject `page < 1` or `limit` outside 1–100 with 422. Omitting `limit` returns all matches.
3. Update the API client types and `listSessions` to pass `page` and `limit` and read `items`.
4. On `SessionsPage`, default to `page: 1` and `limit: 20`. Offer a page size of 10, 20, or 50. Show “Page X of Y” and the visible range (`1–20 of 45`). Previous and Next stay inside the page count. Changing the page size resets to page 1. Put `page` and `limit` in the applied filters so the query key changes.
5. Check your work: seed more sessions than the page size, confirm `total` counts all of the user’s matches, page 2 does not repeat page 1, and another user’s sessions are absent from `items` and from `total`. OpenAPI shows `page` and `limit`.

### Stay in scope

- Leave cursor pagination out. `page` and `limit` are the contract.
- Leave calendar and plan lists unpaged.
- The dashboard may keep its own cap of recent dated sessions (S3-20). It does not have to use this page object.

### Hints

- When `limit` is omitted, ignore a stray `page` greater than 1 and return `page: 1` so old clients that expect a full list still work.
- Empty page past the end can return `items: []` with the real `total` rather than 404.

### Acceptance criteria

- [ ] `GET /sessions` accepts `page` and optional `limit` (1–100) and documents them in OpenAPI
- [ ] The body is `items`, `total`, `page`, and `limit` (`limit` null when unpaged)
- [ ] `total` and `items` include only the current user’s filtered sessions
- [ ] The sessions page has page size, previous, and next

### Suggested paths

`backend/app/api/sessions.py`, `backend/app/schemas/session.py`, `backend/app/repositories/session.py`, `frontend/src/pages/SessionsPage.tsx`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-S1` in the message, for example `S3-S1: short summary`. Never commit `.env` or secrets.

---

## S3-S2 — Ownership API tests

| Field          | Value                          |
| -------------- | ------------------------------ |
| **Type**       | test                           |
| **Week**       | —                              |
| **Priority**   | Stretch                        |
| **Estimate**   | M                              |
| **Depends on** | S3-11, S3-07, S3-12            |

### New here: automated IDOR checks

S3-22 is a manual script. This ticket encodes the same rules in pytest so a later change cannot quietly return someone else’s session. Use FastAPI’s `TestClient` and a database the tests control (the Sprint 2 test setup, or a dependency override). One module that walks the cross-user cases is enough; a full suite waits for Sprint 6.

Cover sessions, plans, and goals. Also assert clone isolation and that the calendar is scoped.

**Docs & tutorials:**

- [FastAPI — testing](https://fastapi.tiangolo.com/tutorial/testing/) — `TestClient` and dependency overrides
- [pytest](https://docs.pytest.org/en/stable/getting-started.html) — one test module, plain asserts
- S3-11 and S3-22 — the status codes and detail strings

### Your task

Add API tests that prove user B cannot read or change user A’s session, plan, or goal. Your deliverable is a test module that fails if ownership regresses.

### Instructions

1. Add `backend/tests/test_ownership.py` (and any shared fixtures you need next to existing tests).
2. Register user A and user B (or insert them). As A, create a session, a plan, and a goal.
3. As B, call GET, PATCH, and DELETE on each id. Expect **404** and the details `Session not found`, `Plan not found`, and `Goal not found`. A missing token on one of those routes expects **401**.
4. As B, `POST /sessions/{A's id}/clone` expects 404. As B, attach A’s session to B’s plan expects 404 `Session not found`.
5. As B, `GET /sessions`, `GET /plans`, `GET /goals`, and `GET /calendar` do not include A’s ids. `GET /calendar` and `GET /sessions` with A’s `plan_id` return an empty collection (200).
6. Clone A’s session as A, change the source, and assert the clone’s items stay as copied (planned kept, actuals null, source edit isolated). This can live in the ownership module or in `backend/tests/test_sessions.py`.
7. Check your work: `pytest` passes, and temporarily pointing a get at `session.get(id)` without `user_id` makes the test fail.

### Stay in scope

- Leave frontend tests and a CI matrix for Sprint 6.
- Leave a second convention (403) out. Assert the 404 details from S3-11.
- These tests call the HTTP API. They do not need to open the React app.

### Hints

- Unique emails per run (a uuid suffix) keep a shared dev database from colliding. A transaction rollback fixture is better if you already have one.
- Assert the JSON `detail` string, not only the status code, so a 404 with a different message still fails.

### Acceptance criteria

- [ ] Tests show B cannot get, update, or delete A’s session, plan, or goal (404 and the S3-11 details)
- [ ] B cannot clone A’s session or attach A’s session
- [ ] Calendar and lists stay on the caller; a foreign `plan_id` filter is an empty 200
- [ ] A clone stays unchanged when the source is edited
- [ ] `pytest` runs without clicking the UI

### Suggested paths

`backend/tests/test_ownership.py`, `backend/tests/test_sessions.py`, `backend/tests/conftest.py`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-S2` in the message, for example `S3-S2: short summary`. Never commit `.env` or secrets.

---

## S3-S3 — Add models to SQLAdmin

| Field          | Value   |
| -------------- | ------- |
| **Type**       | chore   |
| **Week**       | —       |
| **Priority**   | Stretch |
| **Estimate**   | S       |
| **Depends on** | S3-01, S3-02, S3-03, Sprint 2 SQLAdmin |

### New here: admin views for the training log

Sprint 2 mounted SQLAdmin at `/admin` for users, activity types, and unit types. Session, plan, and goal rows are invisible there until you register a `ModelView` for each. That login stays the env username and password. A JWT does not open `/admin`.

Show useful columns (name, user, `session_at`, status, `plan_id`). Keep `password_hash` off the user view, as in Sprint 2. You do not have to inline-edit every measurement in the admin; a list that opens the row is enough for a demo.

**Docs & tutorials:**

- [SQLAdmin — ModelView](https://aminalaee.dev/sqladmin/configurations/) — columns, search, and labels
- [SQLAdmin — adding views](https://aminalaee.dev/sqladmin/) — `admin.add_view`
- Sprint 2 S2-07 — `backend/app/admin.py` and the env login

### Your task

Register the Sprint 3 models in SQLAdmin so a demo can inspect sessions, plans, and goals in the browser. Your deliverable is new `ModelView` classes in `backend/app/admin.py`.

### Instructions

1. Add views for `WorkoutSession`, `WorkoutSessionItem`, `WorkoutSessionMeasurement`, `WorkoutPlan`, and `Goal`.
2. Choose a short name and icon or label per view. Include the foreign keys you need to see ownership (`user_id`, `session_id`, `plan_id`, `unit_type_id`).
3. Leave Sprint 2 views registered. Do not show `password_hash`.
4. Note in a comment next to the views that a new model needs a new view (the habit from Sprint 2).
5. Check your work: log into `/admin` with the env account, open a session you created in the app, and confirm its items and measurements are listed. Confirm the app JWT still does not authenticate `/admin`.

### Stay in scope

- Leave a custom admin dashboard and bulk import out.
- Leave measurement validation in the service layer. Admin is a demo window onto tables, not a second API.
- This ticket does not change ownership on `/sessions`. SQLAdmin is a separate login with full table access for you, the developer.

### Hints

- `column_list` and `column_searchable_list` make the demo faster than the default every-column view.
- If a relationship label crashes the list, use a column property or exclude that relationship and show the foreign key id instead.

### Acceptance criteria

- [ ] `/admin` lists workout sessions, items, measurements, plans, and goals
- [ ] Sprint 2 catalog and user views still load
- [ ] `password_hash` is not a visible column
- [ ] SQLAdmin still uses the env username and password

### Suggested paths

`backend/app/admin.py`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-S3` in the message, for example `S3-S3: short summary`. Never commit `.env` or secrets.

---

## S3-S4 — Planned vs actual adherence preview

| Field          | Value        |
| -------------- | ------------ |
| **Type**       | feature      |
| **Week**       | —            |
| **Priority**   | Stretch      |
| **Estimate**   | M            |
| **Depends on** | S3-05, S3-11 |

### New here: a small planned-vs-actual summary

Sprint 4 will chart progress. This stretch is a **preview**: for the current user, over a date range, compare `planned_value` and `actual_value` on measurements that have both. Keep the math in a **pure function** that takes plain numbers (or small dataclasses) and returns a summary. The HTTP layer only loads that user’s rows and calls the function.

Do not invent a large analytics API. One owner-scoped read is enough, and you choose the path (for example under the sessions or a tiny stats route). Document the path in OpenAPI. Suggested summary fields, which you may trim:

| Field | Meaning |
| ----- | ------- |
| `compared` | measurements in range where both values are present |
| `planned_total` | sum of those planned values |
| `actual_total` | sum of those actual values |
| `hit_count` | how many of those measurements have `actual_value >= planned_value` |

Skip measurements with a null planned or null actual. Ignore other users’ sessions. A reversed `from` / `to` stays **400** `from must not be after to`, matching S3-06. Unscheduled sessions (`session_at` null) are outside every range.

This is a thinking aid for Sprint 4. It is not the chart, the streak counter, or the AI coach.

**Docs & tutorials:**

- [pytest](https://docs.pytest.org/en/stable/getting-started.html) — test the pure function without HTTP
- [FastAPI — query parameters](https://fastapi.tiangolo.com/tutorial/query-params/) — `from` and `to` on the read
- S3-05 — values already live on `workout_session_measurements`

### Your task

Add a testable comparison of planned and actual values for the logged-in user. Your deliverable is a pure function with unit tests, plus a thin owner-scoped endpoint that feeds it.

### Instructions

1. Put the comparison in a function that does not import FastAPI or the database session. Inputs are the caller’s measurements (planned, actual, and the session’s `session_at`). Output is the summary you documented.
2. Unit-test it: both values present, one side null (skipped), actual above and below planned, empty input, and a session outside the range.
3. Add a JWT route that loads only the current user’s measurements in range and returns the summary. Reuse the date-range 400 from S3-06. Another user’s data never enters the function.
4. Document the path and query parameters in OpenAPI. A one-line note in the sprint README or in the route docstring is enough to point Sprint 4 at this preview.
5. Check your work: the unit tests pass without a server. With two users in OpenAPI, the summary counts only the caller’s paired measurements.

### Stay in scope

- Leave charts, weekly buckets, and streaks for Sprint 4. This ticket returns a single summary for a range.
- Leave goals (`target_value`) out of the formula. This compares planned and actual on measurements.
- Keep the route small and document whichever path you choose. A path like `GET /sessions/adherence` must be registered before `GET /sessions/{session_id}`, or FastAPI will treat `adherence` as an id. Building the Sprint 4 stats module waits.

### Hints

- Pass already-filtered rows into the pure function so the test file does not need Postgres.
- Summing across units (km + kg) is a known limitation. Either group by `unit_type_id` or document that the preview sums raw numbers. Grouping by unit is the better preview.

### Acceptance criteria

- [ ] A pure function compares planned and actual and skips nulls
- [ ] Unit tests cover the function without HTTP
- [ ] The endpoint requires a JWT and uses only the caller’s measurements
- [ ] A reversed range returns 400 `from must not be after to`
- [ ] The path is documented for Sprint 4

### Suggested paths

`backend/app/services/sessions.py` or a small helper module next to it, `backend/tests/`, `backend/app/api/sessions.py`

### Commit

When this ticket is done, create a **new Git commit** for it. Do not mix unrelated tickets in the same commit. Put `S3-S4` in the message, for example `S3-S4: short summary`. Never commit `.env` or secrets.

---

## Related

- Previous tickets: [sprint-02-tickets.md](sprint-02-tickets.md)
- Next tickets: [sprint-04-tickets.md](sprint-04-tickets.md)

