from __future__ import annotations

from veriq.application.services.health_service import (
    get_health_status,
    get_version_info,
)


def test_get_health_status() -> None:
    """Description: Validate health service payload structure.
    Parameters:
        None
    Returns:
        None
    Usage Example:
        test_get_health_status()
    """

    payload = get_health_status()
    assert payload["status"] == "ok"
    assert "timestamp" in payload


def test_get_version_info() -> None:
    """Description: Validate version info service output.
    Parameters:
        None
    Returns:
        None
    Usage Example:
        test_get_version_info()
    """

    info = get_version_info()
    assert info.app_name != ""
    assert info.app_version != ""
    assert info.environment != ""
