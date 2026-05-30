from __future__ import annotations

from fastapi import HTTPException


def http_error(status_code: int, detail: str) -> HTTPException:
    """Description: Build an HTTPException with consistent detail.
    Parameters:
        status_code: HTTP status code.
        detail: Error detail message.
    Returns:
        HTTPException: Configured exception instance.
    Usage Example:
        raise http_error(400, "Invalid request")
    """

    return HTTPException(status_code=status_code, detail=detail)
