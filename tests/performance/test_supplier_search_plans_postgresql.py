"""Real PostgreSQL plan qualification using the CI service database."""

import os

import pytest

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.schema import load_persistence_metadata
from tests.performance.supplier_search_plans import characterize_supplier_search

pytestmark = pytest.mark.postgresql


def test_supplier_query_plans_postgresql() -> None:
    url = os.environ.get("PYSRMKIT_POSTGRESQL_TEST_URL")
    if url is None:
        pytest.skip("PYSRMKIT_POSTGRESQL_TEST_URL is not configured")

    engine = create_persistence_engine(url)
    metadata = load_persistence_metadata()
    try:
        metadata.drop_all(engine)
        metadata.create_all(engine)
        characterize_supplier_search(engine)
    finally:
        metadata.drop_all(engine)
        engine.dispose()
