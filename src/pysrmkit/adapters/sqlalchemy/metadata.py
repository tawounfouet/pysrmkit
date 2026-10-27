"""SQLAlchemy metadata owned by the persistence adapter."""

from sqlalchemy.orm import DeclarativeBase


class PersistenceBase(DeclarativeBase):
    """Declarative base for PySRMKit persistence records."""
