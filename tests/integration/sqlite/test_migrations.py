"""SQLite qualification for the Alembic Persistent Core baseline."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import CheckConstraint, UniqueConstraint, inspect
from sqlalchemy.engine import Engine

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.schema import load_persistence_metadata

ALEMBIC_VERSION_TABLE = "alembic_version"


def _alembic_config(database_url: str) -> Config:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    return config


def _assert_migrated_schema_matches_metadata(engine: Engine) -> None:
    metadata = load_persistence_metadata()
    inspector = inspect(engine)

    actual_tables = set(inspector.get_table_names()) - {ALEMBIC_VERSION_TABLE}
    assert actual_tables == set(metadata.tables)

    for table_name, table in metadata.tables.items():
        assert {column["name"] for column in inspector.get_columns(table_name)} == set(
            table.columns.keys()
        )
        assert inspector.get_pk_constraint(table_name)["name"] == table.primary_key.name

        expected_foreign_keys = {constraint.name for constraint in table.foreign_key_constraints}
        actual_foreign_keys = {
            foreign_key["name"] for foreign_key in inspector.get_foreign_keys(table_name)
        }
        assert actual_foreign_keys == expected_foreign_keys

        expected_unique_constraints = {
            constraint.name
            for constraint in table.constraints
            if isinstance(constraint, UniqueConstraint)
        }
        actual_unique_constraints = {
            constraint["name"] for constraint in inspector.get_unique_constraints(table_name)
        }
        assert actual_unique_constraints == expected_unique_constraints

        expected_check_constraints = {
            constraint.name
            for constraint in table.constraints
            if isinstance(constraint, CheckConstraint)
        }
        actual_check_constraints = {
            constraint["name"] for constraint in inspector.get_check_constraints(table_name)
        }
        assert actual_check_constraints == expected_check_constraints

        expected_indexes = {index.name for index in table.indexes}
        actual_indexes = {index["name"] for index in inspector.get_indexes(table_name)}
        assert actual_indexes == expected_indexes


def test_empty_sqlite_database_can_upgrade_to_persistent_core_head(tmp_path: Path) -> None:
    database_path = tmp_path / "pysrmkit.db"
    database_url = f"sqlite:///{database_path}"
    config = _alembic_config(database_url)

    command.upgrade(config, "head")

    engine = create_persistence_engine(database_url)
    try:
        _assert_migrated_schema_matches_metadata(engine)
    finally:
        engine.dispose()


def test_sqlite_baseline_can_downgrade_and_reupgrade(tmp_path: Path) -> None:
    database_path = tmp_path / "pysrmkit-replay.db"
    database_url = f"sqlite:///{database_path}"
    config = _alembic_config(database_url)

    command.upgrade(config, "head")
    command.downgrade(config, "base")

    engine = create_persistence_engine(database_url)
    try:
        remaining_business_tables = set(inspect(engine).get_table_names()) - {ALEMBIC_VERSION_TABLE}
        assert remaining_business_tables == set()
    finally:
        engine.dispose()

    command.upgrade(config, "head")

    engine = create_persistence_engine(database_url)
    try:
        _assert_migrated_schema_matches_metadata(engine)
    finally:
        engine.dispose()
