"""Composition root: construct the FastAPI application.

Run from backend/:

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Then open http://localhost:8000/docs
"""

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="Exercise Progress Tracker")
app.state.settings = settings
app.include_router(health_router)
