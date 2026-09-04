from fastapi import APIRouter, Response, status

from app.schemas.health import DatabaseHealthResponse, HealthResponse
from app.services.health import get_database_health, get_health

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health() -> HealthResponse:
    return get_health()


@router.get("/health/db", response_model=DatabaseHealthResponse)
def health_db(response: Response) -> DatabaseHealthResponse:
    result = get_database_health()
    if result.database != "connected":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return result
