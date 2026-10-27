"""PostgreSQL relational constraints for SupplierQualification persistence."""

import os
from datetime import UTC, datetime

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from tests.contracts.repositories.sqlalchemy_context import prepare_relationship_context

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.repositories.qualification import (
    SqlAlchemySupplierQualificationRepository,
)
from pysrmkit.adapters.sqlalchemy.session import create_session_factory
from pysrmkit.domain.qualification.entities import SupplierQualification
from pysrmkit.domain.qualification.value_objects import (
    QualificationId,
    QualificationScope,
    QualificationStatus,
)
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId
from pysrmkit.domain.supplier.value_objects import CategoryCode

pytestmark = pytest.mark.postgresql
DATABASE_URL = os.environ.get("PYSRMKIT_POSTGRESQL_TEST_URL")
NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


def _session() -> tuple[Session, Engine]:
    if DATABASE_URL is None:
        pytest.skip("PYSRMKIT_POSTGRESQL_TEST_URL is not configured")
    engine = create_persistence_engine(DATABASE_URL)
    PersistenceBase.metadata.drop_all(engine)
    PersistenceBase.metadata.create_all(engine)
    return create_session_factory(engine)(), engine


def _qualification(
    relationship_id: SupplierRelationshipId,
    *,
    status: QualificationStatus = QualificationStatus.PENDING,
) -> SupplierQualification:
    return SupplierQualification.reconstitute(
        qualification_id=QualificationId.new(),
        relationship_id=relationship_id,
        scope=QualificationScope(category_code=CategoryCode("IT_SERVICES")),
        requested_at=NOW,
        status=status,
    )


def test_postgresql_current_qualification_scope_is_unique() -> None:
    session, engine = _session()
    repository = SqlAlchemySupplierQualificationRepository(session)
    relationship_id = SupplierRelationshipId.new()
    prepare_relationship_context(session, relationship_id, label="PostgreSQL Current Scope")

    try:
        repository.save(_qualification(relationship_id))
        session.flush()
        repository.save(_qualification(relationship_id))

        with pytest.raises(IntegrityError):
            session.flush()
    finally:
        session.rollback()
        session.close()
        engine.dispose()


def test_postgresql_expired_history_can_coexist_with_current_qualification() -> None:
    session, engine = _session()
    repository = SqlAlchemySupplierQualificationRepository(session)
    relationship_id = SupplierRelationshipId.new()
    prepare_relationship_context(session, relationship_id, label="PostgreSQL History")
    historical = _qualification(relationship_id, status=QualificationStatus.EXPIRED)
    current = _qualification(relationship_id)

    try:
        repository.save(historical)
        session.flush()
        repository.save(current)
        session.flush()

        loaded = repository.find_current_for_scope(relationship_id, current.scope)

        assert loaded is not None
        assert loaded.id == current.id
    finally:
        session.rollback()
        session.close()
        engine.dispose()
