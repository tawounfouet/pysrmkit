"""SupplierQualificationRepository contract execution for SQLAlchemy SQLite."""

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


class TestSqlAlchemySupplierQualificationRepository(
    SupplierQualificationRepositoryContract
):
    engine: Engine
    session: Session
    repository: SqlAlchemySupplierQualificationRepository

    def setup_method(self) -> None:
        self.engine = create_persistence_engine("sqlite:///:memory:")
        PersistenceBase.metadata.create_all(self.engine)
        self.session = create_session_factory(self.engine)()
        self.repository = SqlAlchemySupplierQualificationRepository(self.session)

    def teardown_method(self) -> None:
        self.session.rollback()
        self.session.close()
        self.engine.dispose()

    def make_repository(self) -> SupplierQualificationRepository:
        return self.repository

    def prepare_qualification(self, qualification: SupplierQualification) -> None:
        prepare_relationship_context(
            self.session,
            qualification.relationship_id,
            label="SQLite Qualification Contract",
        )
