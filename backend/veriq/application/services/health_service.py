from __future__ import annotations

from datetime import UTC, datetime

from veriq.domain.models.version import VersionInfo
from veriq.infrastructure.config.settings import get_settings


def get_health_status() -> dict[str, str]:
    """Description: Build a simple health response with a UTC timestamp.
    Parameters:
        None
    Returns:
        dict[str, str]: Health payload containing status and timestamp.
    Usage Example:
        payload = get_health_status()
    """

    timestamp = datetime.now(UTC).isoformat()
    return {"status": "ok", "timestamp": timestamp}


def get_version_info() -> VersionInfo:
    """Description: Build version info from runtime settings.
    Parameters:
        None
    Returns:
        VersionInfo: Application name, version, and environment.
    Usage Example:
        info = get_version_info()
    """

    settings = get_settings()
    return VersionInfo(
        app_name=settings.app_name,
        app_version=settings.app_version,
        environment=settings.environment,
    )
