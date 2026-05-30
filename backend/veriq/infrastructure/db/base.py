from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Description: Base class for SQLAlchemy ORM models.
    Usage Example:
        class MyModel(Base):
            __tablename__ = "my_table"
    """

    pass
