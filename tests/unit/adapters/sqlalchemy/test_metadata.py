"""SQLAlchemy persistence metadata foundation tests."""

from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase


def test_persistence_metadata_starts_without_speculative_tables() -> None:
    assert tuple(PersistenceBase.metadata.tables) == ()
