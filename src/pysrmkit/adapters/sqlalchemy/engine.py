"""SQLAlchemy Engine creation for PySRMKit persistence adapters."""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.pool import ConnectionPoolEntry


def _enable_sqlite_foreign_keys(
    dbapi_connection: DBAPIConnection,
    _connection_record: ConnectionPoolEntry,
) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


def create_persistence_engine(
    database_url: str,
    *,
    echo: bool = False,
) -> Engine:
    """Create an Engine without connecting during package import.

    SQLite connections enable foreign-key enforcement explicitly.
    """

    engine = create_engine(database_url, echo=echo)
    if engine.dialect.name == "sqlite":
        event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    return engine
