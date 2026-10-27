"""SupplierQualificationRepository contract execution against real PostgreSQL."""

import os

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.repositories.qualification import (
    SqlAlchemySupplierQualificationRepository,
)
from pysrmkit.adapters.sqlalchemy.session import create_session_factory
from pysrmkit.domain.qualification.entities import SupplierQualification
from pysrmkit.ports.repositories.qualification import SupplierQualificationRepository
from tests.contracts.repositories.sqlalchemy_context import prepare_relationship_context
from tests.contracts.repositories.test_qualification_repository_contract import (
    SupplierQualificationRepositoryContract,
)

pytestmark = pytest.mark.postgresql
DATABASE_URL = os.environ.get("PYSRMKIT_POSTGRESQL_TEST_URL")


class TestPostgresqlSupplierQualificationRepository(
    SupplierQualificationRepositoryContract
):
    engine: Engine
    session: Session
    repository: SqlAlchemySupplierQualificationRepository

    def setup_method(self) -> None:
        if DATABASE_URL is None:
            pytest.skip("PYSRMKIT_POSTGRESQL_TEST_URL is not configured")
        self.engine = create_persistence_engine(DATABASE_URL)
        PersistenceBase.metadata.drop_all(self.engine)
        PersistenceBase.metadata.create_all(self.engine)
        self.session = create_session_factory(self.engine)()
        self.repository = SqlAlchemySupplierQualificationRepository(self.session)

    def teardown_method(self) -> None:
        if not hasattr(self, "session"):
            return
        self.session.rollback()
        self.session.close()
        self.engine.dispose()

    def make_repository(self) -> SupplierQualificationRepository:
        return self.repository

    def prepare_qualification(self, qualification: SupplierQualification) -> None:
        prepare_relationship_context(
            self.session,
            qualification.relationship_id,
            label="PostgreSQL Qualification Contract",
        )
