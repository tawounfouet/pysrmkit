"""SupplierOnboardingRepository contract execution against real PostgreSQL."""

import os

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.repositories.onboarding import (
    SqlAlchemySupplierOnboardingRepository,
)
from pysrmkit.adapters.sqlalchemy.session import create_session_factory
from pysrmkit.domain.onboarding.entities import SupplierOnboarding
from pysrmkit.ports.repositories.onboarding import SupplierOnboardingRepository
from tests.contracts.repositories.sqlalchemy_context import prepare_relationship_context
from tests.contracts.repositories.test_onboarding_repository_contract import (
    SupplierOnboardingRepositoryContract,
)

pytestmark = pytest.mark.postgresql
DATABASE_URL = os.environ.get("PYSRMKIT_POSTGRESQL_TEST_URL")


class TestPostgresqlSupplierOnboardingRepository(SupplierOnboardingRepositoryContract):
    engine: Engine
    session: Session
    repository: SqlAlchemySupplierOnboardingRepository

    def setup_method(self) -> None:
        if DATABASE_URL is None:
            pytest.skip("PYSRMKIT_POSTGRESQL_TEST_URL is not configured")
        self.engine = create_persistence_engine(DATABASE_URL)
        PersistenceBase.metadata.drop_all(self.engine)
        PersistenceBase.metadata.create_all(self.engine)
        self.session = create_session_factory(self.engine)()
        self.repository = SqlAlchemySupplierOnboardingRepository(self.session)

    def teardown_method(self) -> None:
        if not hasattr(self, "session"):
            return
        self.session.rollback()
        self.session.close()
        self.engine.dispose()

    def make_repository(self) -> SupplierOnboardingRepository:
        return self.repository

    def prepare_onboarding(self, onboarding: SupplierOnboarding) -> None:
        prepare_relationship_context(
            self.session,
            onboarding.relationship_id,
            label="PostgreSQL Onboarding Contract",
        )
