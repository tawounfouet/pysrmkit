"""Transaction-boundary tests for SQLAlchemy repositories."""

from sqlalchemy import event
from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.repositories.supplier import SqlAlchemySupplierRepository
from pysrmkit.adapters.sqlalchemy.session import create_session_factory
from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import SupplierId, SupplierIdentity


def test_repository_save_does_not_commit_session() -> None:
    engine = create_persistence_engine("sqlite:///:memory:")
    PersistenceBase.metadata.create_all(engine)
    session = create_session_factory(engine)()
    commits = 0

    def record_commit(_session: Session) -> None:
        nonlocal commits
        commits += 1

    event.listen(session, "after_commit", record_commit)

    try:
        repository = SqlAlchemySupplierRepository(session)
        repository.save(
            Supplier.reconstitute(
                supplier_id=SupplierId.new(),
                identity=SupplierIdentity(legal_name="No Auto Commit"),
            )
        )
        session.flush()

        assert commits == 0
        assert session.in_transaction() is True
    finally:
        session.rollback()
        session.close()
        engine.dispose()
