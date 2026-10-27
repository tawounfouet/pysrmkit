"""SQLite relational constraints for SupplierQualification persistence."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from tests.contracts.repositories.sqlalchemy_context import prepare_relationship_context

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.models.qualification import SupplierQualificationRecord
from pysrmkit.adapters.sqlalchemy.repositories.qualification import (
    SqlAlchemySupplierQualificationRepository,
)
from pysrmkit.adapters.sqlalchemy.session import create_session_factory
from pysrmkit.domain.qualification.entities import SupplierQualification
from pysrmkit.domain.qualification.value_objects import (
    QualificationDecision,
    QualificationId,
    QualificationScope,
    QualificationStatus,
)
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId
from pysrmkit.domain.supplier.value_objects import CategoryCode

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
LATER = datetime(2026, 10, 27, 13, 0, tzinfo=UTC)


def _session() -> tuple[Session, Engine]:
    engine = create_persistence_engine("sqlite:///:memory:")
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


def test_qualification_requires_existing_relationship() -> None:
    session, engine = _session()
    repository = SqlAlchemySupplierQualificationRepository(session)
    qualification = _qualification(SupplierRelationshipId.new())

    try:
        repository.save(qualification)

        with pytest.raises(IntegrityError):
            session.flush()
    finally:
        session.rollback()
        session.close()
        engine.dispose()


def test_database_rejects_empty_qualification_scope() -> None:
    session, engine = _session()
    relationship_id = SupplierRelationshipId.new()
    prepare_relationship_context(session, relationship_id, label="SQLite Empty Scope")

    try:
        session.add(
            SupplierQualificationRecord(
                qualification_id=uuid4(),
                relationship_id=relationship_id.value,
                scope_organization_id="",
                scope_category_code="",
                scope_country_code="",
                requested_at=NOW,
                status=QualificationStatus.PENDING.value,
            )
        )

        with pytest.raises(IntegrityError):
            session.flush()
    finally:
        session.rollback()
        session.close()
        engine.dispose()


def test_current_qualification_scope_is_unique() -> None:
    session, engine = _session()
    repository = SqlAlchemySupplierQualificationRepository(session)
    relationship_id = SupplierRelationshipId.new()
    prepare_relationship_context(session, relationship_id, label="SQLite Current Scope")

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


def test_expired_history_can_coexist_with_new_current_qualification() -> None:
    session, engine = _session()
    repository = SqlAlchemySupplierQualificationRepository(session)
    relationship_id = SupplierRelationshipId.new()
    prepare_relationship_context(session, relationship_id, label="SQLite Historical Scope")
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


def test_decision_timestamps_and_explanation_survive_sqlite_round_trip() -> None:
    session, engine = _session()
    repository = SqlAlchemySupplierQualificationRepository(session)
    relationship_id = SupplierRelationshipId.new()
    prepare_relationship_context(session, relationship_id, label="SQLite Decision")
    qualification = _qualification(relationship_id)
    decision = QualificationDecision(
        approved=False,
        resulting_status=QualificationStatus.NOT_QUALIFIED,
        reasons=("Score below threshold", "Missing required evidence"),
        failed_requirements=("ASSESSMENT_MINIMUM_SCORE", "REQUIRED_ANSWERS_COMPLETE"),
        decided_at=LATER,
    )
    qualification.apply_decision(decision)
    qualification.pull_events()

    try:
        repository.save(qualification)
        session.flush()
        session.expire_all()

        loaded = repository.get(qualification.id)

        assert loaded is not None
        assert loaded.requested_at == NOW
        assert loaded.requested_at.tzinfo is not None
        assert loaded.decision == decision
        assert loaded.decision is not None
        assert loaded.decision.decided_at.tzinfo is not None
    finally:
        session.rollback()
        session.close()
        engine.dispose()


def test_database_rejects_partial_decision_columns() -> None:
    session, engine = _session()
    relationship_id = SupplierRelationshipId.new()
    prepare_relationship_context(session, relationship_id, label="SQLite Partial Decision")

    try:
        session.add(
            SupplierQualificationRecord(
                qualification_id=uuid4(),
                relationship_id=relationship_id.value,
                scope_organization_id="",
                scope_category_code="IT_SERVICES",
                scope_country_code="",
                requested_at=NOW,
                status=QualificationStatus.QUALIFIED.value,
                decision_approved=True,
            )
        )

        with pytest.raises(IntegrityError):
            session.flush()
    finally:
        session.rollback()
        session.close()
        engine.dispose()
