"""A3-05: execute the unmodified Supplier search contract on real PostgreSQL.

Tests are collected only in the PostgreSQL CI job. They reuse the exact
ASCII oracle already qualified on InMemory and SQLite in A3-01.
"""

import os

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.repositories.supplier import SqlAlchemySupplierRepository
from pysrmkit.adapters.sqlalchemy.schema import load_persistence_metadata
from pysrmkit.adapters.sqlalchemy.session import create_session_factory
from tests.contracts.queries.corpus import SearchableSupplierRepository
from tests.contracts.queries.test_supplier_search_contract import SupplierSearchContract

pytestmark = pytest.mark.postgresql
DATABASE_URL = os.environ.get("PYSRMKIT_POSTGRESQL_TEST_URL")


class TestPostgresqlSupplierSearchContract(SupplierSearchContract):
    """PostgreSQL adapter joins the same contract through one factory method."""

    engine: Engine
    session: Session
    repository: SqlAlchemySupplierRepository

    def setup_method(self) -> None:
        if DATABASE_URL is None:
            pytest.skip("PYSRMKIT_POSTGRESQL_TEST_URL is not configured")

        self.engine = create_persistence_engine(DATABASE_URL)
        metadata = load_persistence_metadata()
        metadata.drop_all(self.engine)
        metadata.create_all(self.engine)
        self.session = create_session_factory(self.engine)()
        self.repository = SqlAlchemySupplierRepository(self.session)

    def teardown_method(self) -> None:
        if not hasattr(self, "session"):
            return
        self.session.rollback()
        self.session.close()
        self.engine.dispose()

    def make_repository(self) -> SearchableSupplierRepository:
        return self.repository
