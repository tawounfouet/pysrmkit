"""PostgreSQL qualification for the Alembic Persistent Core baseline."""

from __future__ import annotations

import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.schema import load_persistence_metadata

DATABASE_URL = os.getenv("PYSRMKIT_POSTGRESQL_TEST_URL")


def _alembic_config(database_url: str) -> Config:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    return config


@pytest.mark.postgresql
def test_postgresql_empty_database_can_upgrade_to_persistent_core_head() -> None:
    if DATABASE_URL is None:
        pytest.skip("PYSRMKIT_POSTGRESQL_TEST_URL is not configured")

    metadata = load_persistence_metadata()
    engine = create_persistence_engine(DATABASE_URL)

    try:
        metadata.drop_all(engine)
        with engine.begin() as connection:
            connection.exec_driver_sql("DROP TABLE IF EXISTS alembic_version")

        config = _alembic_config(DATABASE_URL)
        command.upgrade(config, "head")
        command.upgrade(config, "head")

        inspector = inspect(engine)
        actual_tables = set(inspector.get_table_names()) - {"alembic_version"}
        assert actual_tables == set(metadata.tables)

        for table_name, table in metadata.tables.items():
            assert {column["name"] for column in inspector.get_columns(table_name)} == set(
                table.columns.keys()
            )
            assert inspector.get_pk_constraint(table_name)["name"] == table.primary_key.name
            assert {
                foreign_key["name"] for foreign_key in inspector.get_foreign_keys(table_name)
            } == {constraint.name for constraint in table.foreign_key_constraints}
            assert {index["name"] for index in inspector.get_indexes(table_name)} == {
                index.name for index in table.indexes
            }
    finally:
        metadata.drop_all(engine)
        with engine.begin() as connection:
            connection.exec_driver_sql("DROP TABLE IF EXISTS alembic_version")
        engine.dispose()
