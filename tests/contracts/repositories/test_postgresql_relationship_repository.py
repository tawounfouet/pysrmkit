"""SupplierRelationshipRepository contract execution against real PostgreSQL."""

import os

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.repositories.relationship import (
    SqlAlchemySupplierRelationshipRepository,
)
from pysrmkit.adapters.sqlalchemy.repositories.supplier import SqlAlchemySupplierRepository
from pysrmkit.adapters.sqlalchemy.session import create_session_factory
from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import SupplierIdentity
from pysrmkit.ports.repositories.relationship import SupplierRelationshipRepository
from tests.contracts.repositories.test_relationship_repository_contract import (
    SupplierRelationshipRepositoryContract,
)

pytestmark = pytest.mark.postgresql
DATABASE_URL = os.environ.get("PYSRMKIT_POSTGRESQL_TEST_URL")


class TestPostgresqlSupplierRelationshipRepository(SupplierRelationshipRepositoryContract):
    engine: Engine
    session: Session
    repository: SqlAlchemySupplierRelationshipRepository
    supplier_repository: SqlAlchemySupplierRepository

    def setup_method(self) -> None:
        if DATABASE_URL is None:
            pytest.skip("PYSRMKIT_POSTGRESQL_TEST_URL is not configured")
        self.engine = create_persistence_engine(DATABASE_URL)
        PersistenceBase.metadata.drop_all(self.engine)
        PersistenceBase.metadata.create_all(self.engine)
        self.session = create_session_factory(self.engine)()
        self.repository = SqlAlchemySupplierRelationshipRepository(self.session)
        self.supplier_repository = SqlAlchemySupplierRepository(self.session)

    def teardown_method(self) -> None:
        if not hasattr(self, "session"):
            return
        self.session.rollback()
        self.session.close()
        self.engine.dispose()

    def make_repository(self) -> SupplierRelationshipRepository:
        return self.repository

    def prepare_relationship(self, relationship: SupplierRelationship) -> None:
        if self.supplier_repository.get(relationship.supplier_id) is not None:
            return
        self.supplier_repository.save(
            Supplier.reconstitute(
                supplier_id=relationship.supplier_id,
                identity=SupplierIdentity(
                    legal_name=f"PostgreSQL Contract Supplier {relationship.supplier_id}"
                ),
            )
        )
