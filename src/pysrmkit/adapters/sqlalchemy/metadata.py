"""SQLAlchemy metadata owned by the persistence adapter."""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

PERSISTENCE_NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s",
    "pk": "pk_%(table_name)s",
}


class PersistenceBase(DeclarativeBase):
    """Declarative base for PySRMKit persistence records."""

    metadata = MetaData(naming_convention=PERSISTENCE_NAMING_CONVENTION)
