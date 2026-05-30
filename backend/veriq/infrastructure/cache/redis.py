from __future__ import annotations

from redis import Redis

from veriq.infrastructure.config.settings import get_settings


def get_redis_client() -> Redis:
    """Description: Create a Redis client from runtime settings.
    Parameters:
        None
    Returns:
        Redis: Configured Redis client.
    Usage Example:
        client = get_redis_client()
    """

    settings = get_settings()
    return Redis.from_url(settings.redis_url)
