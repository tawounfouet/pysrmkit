"""Qualification for the integration bootstrap routine."""

import pytest
from examples.bootstrap_integration import (
    DEFAULT_NEXT_DASHBOARD_DB_URL,
    DEFAULT_PYSRMKIT_DB_URL,
    bootstrap,
    ensure_database_exists,
)

pytestmark = pytest.mark.integration


def test_ensure_database_exists_is_idempotent() -> None:
    # Since the databases already exist in the local environment, it should return False
    assert ensure_database_exists(DEFAULT_PYSRMKIT_DB_URL) is False
    assert ensure_database_exists(DEFAULT_NEXT_DASHBOARD_DB_URL) is False


def test_bootstrap_is_idempotent() -> None:
    result = bootstrap(seed_nextjs=False)

    assert result["pysrmkit_db_created"] is False
    assert result["nextjs_db_created"] is False
    assert result["suppliers_created"] == 0
    assert result["suppliers_skipped"] == 8
