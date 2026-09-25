"""Composition root: construct the FastAPI application.

Run from backend/:

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Then open http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.admin import setup_admin
from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="Exercise Progress Tracker")
app.state.settings = settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.sqladmin_secret_key)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(sessions_router)
setup_admin(app)
