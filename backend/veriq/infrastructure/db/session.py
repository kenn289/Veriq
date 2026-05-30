from __future__ import annotations

from functools import lru_cache
from typing import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from veriq.infrastructure.config.settings import get_settings


@lru_cache
def get_engine() -> Engine:
    """Description: Create and cache the SQLAlchemy engine.
    Parameters:
        None
    Returns:
        Engine: SQLAlchemy engine instance.
    Usage Example:
        engine = get_engine()
    """

    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True)


def get_session_factory() -> sessionmaker[Session]:
    """Description: Build a session factory bound to the engine.
    Parameters:
        None
    Returns:
        sessionmaker[Session]: Configured session factory.
    Usage Example:
        SessionLocal = get_session_factory()
    """

    engine = get_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db_session() -> Generator[Session, None, None]:
    """Description: Yield a database session for request-scoped usage.
    Parameters:
        None
    Returns:
        Generator[Session, None, None]: Session generator.
    Usage Example:
        for session in get_db_session():
            session.execute("SELECT 1")
    """

    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
