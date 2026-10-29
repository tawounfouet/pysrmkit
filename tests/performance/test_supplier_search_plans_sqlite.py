"""SQLite plan qualification using production Supplier query statements."""

from sqlalchemy import create_engine

from pysrmkit.adapters.sqlalchemy.schema import load_persistence_metadata
from tests.performance.supplier_search_plans import characterize_supplier_search


def test_supplier_query_plans_sqlite() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    load_persistence_metadata().create_all(engine)
    try:
        characterize_supplier_search(engine)
    finally:
        engine.dispose()
