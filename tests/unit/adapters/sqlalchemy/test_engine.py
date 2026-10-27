"""SQLAlchemy persistence Engine foundation tests."""

import pytest
from sqlalchemy import Column, ForeignKey, Integer, MetaData, Table
from sqlalchemy.exc import IntegrityError

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine


def test_sqlite_engine_enables_foreign_key_enforcement() -> None:
    engine = create_persistence_engine("sqlite:///:memory:")

    try:
        with engine.connect() as connection:
            enabled = connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one()

        assert enabled == 1
    finally:
        engine.dispose()


def test_sqlite_engine_enforces_foreign_key_constraints() -> None:
    engine = create_persistence_engine("sqlite:///:memory:")
    metadata = MetaData()
    parent = Table(
        "parent",
        metadata,
        Column("id", Integer, primary_key=True),
    )
    child = Table(
        "child",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("parent_id", Integer, ForeignKey("parent.id"), nullable=False),
    )
    metadata.create_all(engine)

    try:
        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                connection.execute(child.insert().values(id=1, parent_id=999))
    finally:
        engine.dispose()
