"""SupplierRelationshipRepository contract execution for SQLAlchemy SQLite."""

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


class TestSqlAlchemySupplierRelationshipRepository(SupplierRelationshipRepositoryContract):
    engine: Engine
    session: Session
    repository: SqlAlchemySupplierRelationshipRepository
    supplier_repository: SqlAlchemySupplierRepository

    def setup_method(self) -> None:
        self.engine = create_persistence_engine("sqlite:///:memory:")
        PersistenceBase.metadata.create_all(self.engine)
        self.session = create_session_factory(self.engine)()
        self.repository = SqlAlchemySupplierRelationshipRepository(self.session)
        self.supplier_repository = SqlAlchemySupplierRepository(self.session)

    def teardown_method(self) -> None:
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
                    legal_name=f"Contract Supplier {relationship.supplier_id}"
                ),
            )
        )
