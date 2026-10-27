"""SupplierOnboardingRepository contract execution for SQLAlchemy SQLite."""

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


class TestSqlAlchemySupplierOnboardingRepository(SupplierOnboardingRepositoryContract):
    engine: Engine
    session: Session
    repository: SqlAlchemySupplierOnboardingRepository

    def setup_method(self) -> None:
        self.engine = create_persistence_engine("sqlite:///:memory:")
        PersistenceBase.metadata.create_all(self.engine)
        self.session = create_session_factory(self.engine)()
        self.repository = SqlAlchemySupplierOnboardingRepository(self.session)

    def teardown_method(self) -> None:
        self.session.rollback()
        self.session.close()
        self.engine.dispose()

    def make_repository(self) -> SupplierOnboardingRepository:
        return self.repository

    def prepare_onboarding(self, onboarding: SupplierOnboarding) -> None:
        prepare_relationship_context(
            self.session,
            onboarding.relationship_id,
            label="SQLite Onboarding Contract",
        )
