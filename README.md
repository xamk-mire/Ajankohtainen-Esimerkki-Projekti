# Exercise Progress Tracker

This repository is a monorepo for the Exercise Progress Tracker course project: `backend/` will hold the FastAPI API, `frontend/` the React (Vite + TypeScript) SPA, and `docs/` the sprint tickets, templates, and course materials. Later tickets in Sprint 1 will add Docker Compose and a placeholder UI; this README is only a layout stub until S1-13.

## Run the API

From `backend/` (after FastAPI and Uvicorn are installed — S1-04):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs for the interactive OpenAPI UI.
