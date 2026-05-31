from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Description: Health check response payload.
    Usage Example:
        response = HealthResponse(status="ok", timestamp="2026-05-30T12:00:00+00:00")
    """

    status: str = Field(..., description="Service status indicator.")
    timestamp: str = Field(..., description="UTC timestamp in ISO 8601 format.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"status": "ok", "timestamp": "2026-05-30T12:00:00+00:00"}
        }
    )


class VersionResponse(BaseModel):
    """Description: Version response payload.
    Usage Example:
        response = VersionResponse(
            app_name="Veriq API", app_version="0.1.0", environment="development"
        )
    """

    app_name: str = Field(..., description="Application name.")
    app_version: str = Field(..., description="Application version string.")
    environment: str = Field(..., description="Runtime environment name.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "app_name": "Veriq API",
                "app_version": "0.1.0",
                "environment": "development",
            }
        }
    )
