"""SupplierRepository contract execution for the SQLAlchemy SQLite adapter."""

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.repositories.supplier import SqlAlchemySupplierRepository
from pysrmkit.adapters.sqlalchemy.session import create_session_factory
from pysrmkit.ports.repositories.supplier import SupplierRepository
from tests.contracts.repositories.test_supplier_repository_contract import (
    SupplierRepositoryContract,
)


class TestSqlAlchemySupplierRepository(SupplierRepositoryContract):
    engine: Engine
    session: Session
    repository: SqlAlchemySupplierRepository

    def setup_method(self) -> None:
        self.engine = create_persistence_engine("sqlite:///:memory:")
        PersistenceBase.metadata.create_all(self.engine)
        self.session = create_session_factory(self.engine)()
        self.repository = SqlAlchemySupplierRepository(self.session)

    def teardown_method(self) -> None:
        self.session.close()
        self.engine.dispose()

    def make_repository(self) -> SupplierRepository:
        return self.repository
