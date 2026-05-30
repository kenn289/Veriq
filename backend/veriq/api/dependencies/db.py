from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from veriq.infrastructure.db.session import get_db_session


def get_session() -> Generator[Session, None, None]:
    """Description: FastAPI dependency providing a database session.
    Parameters:
        None
    Returns:
        Generator[Session, None, None]: Session generator.
    Usage Example:
        session = Depends(get_session)
    """

    yield from get_db_session()
