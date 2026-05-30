from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VersionInfo:
    """Description: Immutable version information for the running service.
    Usage Example:
        info = VersionInfo(app_name="Veriq API", app_version="0.1.0", environment="development")
    """

    app_name: str
    app_version: str
    environment: str
