"""SupplierAssessmentRepository contract execution for SQLAlchemy SQLite."""

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.repositories.assessment import (
    SqlAlchemySupplierAssessmentRepository,
)
from pysrmkit.adapters.sqlalchemy.session import create_session_factory
from pysrmkit.domain.assessment.entities import SupplierAssessment
from pysrmkit.ports.repositories.assessment import SupplierAssessmentRepository
from tests.contracts.repositories.sqlalchemy_context import prepare_relationship_context
from tests.contracts.repositories.test_assessment_repository_contract import (
    SupplierAssessmentRepositoryContract,
)


class TestSqlAlchemySupplierAssessmentRepository(SupplierAssessmentRepositoryContract):
    engine: Engine
    session: Session
    repository: SqlAlchemySupplierAssessmentRepository

    def setup_method(self) -> None:
        self.engine = create_persistence_engine("sqlite:///:memory:")
        PersistenceBase.metadata.create_all(self.engine)
        self.session = create_session_factory(self.engine)()
        self.repository = SqlAlchemySupplierAssessmentRepository(self.session)

    def teardown_method(self) -> None:
        self.session.rollback()
        self.session.close()
        self.engine.dispose()

    def make_repository(self) -> SupplierAssessmentRepository:
        return self.repository

    def prepare_assessment(self, assessment: SupplierAssessment) -> None:
        prepare_relationship_context(
            self.session,
            assessment.relationship_id,
            label="SQLite Assessment Contract",
        )
