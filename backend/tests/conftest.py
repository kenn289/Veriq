from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from veriq.api.dependencies.db import get_session
from veriq.infrastructure.db.base import Base
from veriq.infrastructure.db import models  # noqa: F401
from veriq.infrastructure.db.seed import seed_roles
from veriq.main import create_app


@pytest.fixture()
def db_session() -> Session:
    """Description: Provide a transient SQLite session for tests.
    Parameters:
        None
    Returns:
        Session: SQLAlchemy session.
    Usage Example:
        session = db_session
    """

    from sqlalchemy import event
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
    session = SessionLocal()
    seed_roles(session)
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    """Description: Provide a FastAPI client wired to the test database.
    Parameters:
        db_session: Database session.
    Returns:
        TestClient: Configured client.
    Usage Example:
        client = client
    """

    app = create_app(seed_roles_on_startup=False)

    def _override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = _override_get_session
    return TestClient(app)
