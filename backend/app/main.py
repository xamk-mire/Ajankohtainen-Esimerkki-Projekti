"""Composition root: construct the FastAPI application.

Run from backend/:

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Then open http://localhost:8000/docs
"""

from fastapi import FastAPI

app = FastAPI(title="Exercise Progress Tracker")
