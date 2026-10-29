"""Qualification for the integration bootstrap routine."""

import pytest
from sqlalchemy import text

from examples.bootstrap_integration import (
    DEFAULT_NEXT_DASHBOARD_DB_URL,
    DEFAULT_PYSRMKIT_DB_URL,
    bootstrap,
    ensure_database_exists,
)
from examples.seed_suppliers import SOURCE_SYSTEM, SUPPLIERS
from pysrmkit import PySRMKit
from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine

pytestmark = pytest.mark.integration


def test_ensure_database_exists_is_idempotent() -> None:
    # The CI bootstrap has already provisioned the databases.
    assert ensure_database_exists(DEFAULT_PYSRMKIT_DB_URL) is False
    assert ensure_database_exists(DEFAULT_NEXT_DASHBOARD_DB_URL) is False


def _persistent_seed_snapshot() -> tuple[tuple[str, str, str], ...]:
    """Capture stable UUID/vendor-code/name tuples through the public Facade."""
    engine = create_persistence_engine(DEFAULT_PYSRMKIT_DB_URL)
    try:
        page = PySRMKit.sql(engine).suppliers.list(offset=0, limit=100)
        assert page.total == len(SUPPLIERS)
        result = []
        for supplier in page.items:
            identifiers = [
                identifier.value
                for identifier in supplier.external_identifiers
                if identifier.kind == "LOCAL_VENDOR_CODE"
                and identifier.source_system == SOURCE_SYSTEM
            ]
            assert len(identifiers) == 1
            result.append((str(supplier.supplier_id), identifiers[0], supplier.legal_name))
        assert len({item[1] for item in result}) == len(SUPPLIERS)
        return tuple(sorted(result))
    finally:
        engine.dispose()


def _alembic_revision() -> str:
    """Read committed migration revision without relying on CLI output."""
    engine = create_persistence_engine(DEFAULT_PYSRMKIT_DB_URL)
    try:
        with engine.connect() as connection:
            revisions = connection.execute(text("SELECT version_num FROM alembic_version")).scalars().all()
        assert len(revisions) == 1
        return revisions[0]
    finally:
        engine.dispose()


def test_full_bootstrap_repeated_runs_preserve_ids_and_migration() -> None:
    """A5-02: two fresh bootstrap executions must not create duplicates."""
    before = _persistent_seed_snapshot()
    revision_before = _alembic_revision()

    first = bootstrap(seed_nextjs=False)
    after_first = _persistent_seed_snapshot()
    revision_after_first = _alembic_revision()

    second = bootstrap(seed_nextjs=False)
    after_second = _persistent_seed_snapshot()
    revision_after_second = _alembic_revision()

    for result in (first, second):
        assert result["pysrmkit_db_created"] is False
        assert result["nextjs_db_created"] is False
        assert result["suppliers_created"] == 0
        assert result["suppliers_skipped"] == len(SUPPLIERS)
        assert result["nextjs_seeded"] is False

    assert before == after_first == after_second
    assert revision_before == revision_after_first == revision_after_second
    assert {item[1] for item in before} == {supplier.vendor_code for supplier in SUPPLIERS}
