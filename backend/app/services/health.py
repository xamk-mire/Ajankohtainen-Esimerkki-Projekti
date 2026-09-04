from app.repositories.health import ping_database
from app.schemas.health import DatabaseHealthResponse, HealthResponse


def get_health() -> HealthResponse:
    return HealthResponse(status="ok")


def get_database_health() -> DatabaseHealthResponse:
    if ping_database():
        return DatabaseHealthResponse(status="ok", database="connected")
    return DatabaseHealthResponse(status="unavailable", database="not connected")
