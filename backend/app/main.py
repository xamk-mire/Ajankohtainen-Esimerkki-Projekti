"""Composition root: construct the FastAPI application.

Run from backend/:

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Then open http://localhost:8000/docs
"""

from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(title="Exercise Progress Tracker")
app.include_router(health_router)
