"""Alembic environment for the PySRMKit persistence adapter."""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from pysrmkit.adapters.sqlalchemy.schema import load_persistence_metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = os.getenv("PYSRMKIT_DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

target_metadata = load_persistence_metadata()


def _configured_database_url() -> str:
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        raise RuntimeError(
            "Database URL is required. Set PYSRMKIT_DATABASE_URL or Alembic sqlalchemy.url."
        )
    return url


def run_migrations_offline() -> None:
    """Run migrations without creating an Engine."""

    context.configure(
        url=_configured_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against an Engine created from Alembic configuration."""

    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _configured_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
