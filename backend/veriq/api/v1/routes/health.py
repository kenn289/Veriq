from __future__ import annotations

from fastapi import APIRouter

from veriq.api.v1.schemas.health import HealthResponse, VersionResponse
from veriq.application.services.health_service import (
    get_health_status,
    get_version_info,
)

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health_check() -> HealthResponse:
    """Description: Report service health and a UTC timestamp.
    Parameters:
        None
    Returns:
        HealthResponse: Health payload with status and timestamp.
    Usage Example:
        response = health_check()
    Request Schema:
        None
    Response Schema:
        HealthResponse { status: str, timestamp: str }
    Examples:
        {"status": "ok", "timestamp": "2026-05-30T12:00:00+00:00"}
    Error Cases:
        - 500: Internal Server Error
    """

    payload = get_health_status()
    return HealthResponse(**payload)


@router.get("/version", response_model=VersionResponse, summary="Version info")
def version_check() -> VersionResponse:
    """Description: Report application name, version, and environment.
    Parameters:
        None
    Returns:
        VersionResponse: Version payload with name, version, and environment.
    Usage Example:
        response = version_check()
    Request Schema:
        None
    Response Schema:
        VersionResponse { app_name: str, app_version: str, environment: str }
    Examples:
        {"app_name": "Veriq API", "app_version": "0.1.0", "environment": "development"}
    Error Cases:
        - 500: Internal Server Error
    """

    info = get_version_info()
    return VersionResponse(
        app_name=info.app_name,
        app_version=info.app_version,
        environment=info.environment,
    )
