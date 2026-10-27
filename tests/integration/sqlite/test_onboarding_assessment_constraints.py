"""SQLite relational constraints for Onboarding and Assessment persistence."""

from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.metadata import PersistenceBase
from pysrmkit.adapters.sqlalchemy.models.assessment import AssessmentAnswerRecord
from pysrmkit.adapters.sqlalchemy.repositories.assessment import (
    SqlAlchemySupplierAssessmentRepository,
)
from pysrmkit.adapters.sqlalchemy.repositories.onboarding import (
    SqlAlchemySupplierOnboardingRepository,
)
from pysrmkit.adapters.sqlalchemy.repositories.relationship import (
    SqlAlchemySupplierRelationshipRepository,
)
from pysrmkit.adapters.sqlalchemy.repositories.supplier import SqlAlchemySupplierRepository
from pysrmkit.adapters.sqlalchemy.session import create_session_factory
from pysrmkit.domain.assessment.entities import SupplierAssessment
from pysrmkit.domain.assessment.value_objects import (
    AssessmentId,
    AssessmentQuestion,
    AssessmentType,
)
from pysrmkit.domain.onboarding.entities import SupplierOnboarding
from pysrmkit.domain.onboarding.value_objects import OnboardingId
from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import SupplierId, SupplierIdentity

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


def _new_session() -> tuple[Session, object]:
    engine = create_persistence_engine("sqlite:///:memory:")
    PersistenceBase.metadata.create_all(engine)
    return create_session_factory(engine)(), engine


def _prepare_relationship(
    session: Session,
    relationship_id: SupplierRelationshipId,
) -> None:
    supplier = Supplier.reconstitute(
        supplier_id=SupplierId.new(),
        identity=SupplierIdentity(legal_name="Constraint Supplier"),
    )
    SqlAlchemySupplierRepository(session).save(supplier)
    SqlAlchemySupplierRelationshipRepository(session).save(
        SupplierRelationship.reconstitute(
            relationship_id=relationship_id,
            supplier_id=supplier.id,
            organization_id=InternalOrganizationId("ORG-CONSTRAINT"),
        )
    )
    session.flush()


def test_onboarding_requires_existing_relationship() -> None:
    session, engine = _new_session()
    repository = SqlAlchemySupplierOnboardingRepository(session)
    onboarding = SupplierOnboarding.reconstitute(
        onboarding_id=OnboardingId.new(),
        relationship_id=SupplierRelationshipId.new(),
        started_at=NOW,
    )

    try:
        repository.save(onboarding)

        with pytest.raises(IntegrityError):
            session.flush()
    finally:
        session.rollback()
        session.close()
        engine.dispose()


def test_only_one_onboarding_can_exist_for_relationship() -> None:
    session, engine = _new_session()
    relationship_id = SupplierRelationshipId.new()
    _prepare_relationship(session, relationship_id)
    repository = SqlAlchemySupplierOnboardingRepository(session)

    try:
        repository.save(
            SupplierOnboarding.reconstitute(
                onboarding_id=OnboardingId.new(),
                relationship_id=relationship_id,
                started_at=NOW,
            )
        )
        session.flush()
        repository.save(
            SupplierOnboarding.reconstitute(
                onboarding_id=OnboardingId.new(),
                relationship_id=relationship_id,
                started_at=NOW,
            )
        )

        with pytest.raises(IntegrityError):
            session.flush()
    finally:
        session.rollback()
        session.close()
        engine.dispose()


def test_assessment_requires_existing_relationship() -> None:
    session, engine = _new_session()
    repository = SqlAlchemySupplierAssessmentRepository(session)
    assessment = SupplierAssessment.reconstitute(
        assessment_id=AssessmentId.new(),
        relationship_id=SupplierRelationshipId.new(),
        assessment_type=AssessmentType("QUESTIONNAIRE"),
        created_at=NOW,
        questions=(AssessmentQuestion(code="LEGAL"),),
    )

    try:
        repository.save(assessment)

        with pytest.raises(IntegrityError):
            session.flush()
    finally:
        session.rollback()
        session.close()
        engine.dispose()


def test_assessment_answer_requires_existing_question_row() -> None:
    session, engine = _new_session()
    relationship_id = SupplierRelationshipId.new()
    _prepare_relationship(session, relationship_id)
    assessment = SupplierAssessment.reconstitute(
        assessment_id=AssessmentId.new(),
        relationship_id=relationship_id,
        assessment_type=AssessmentType("QUESTIONNAIRE"),
        created_at=NOW,
        questions=(AssessmentQuestion(code="LEGAL"),),
    )

    try:
        SqlAlchemySupplierAssessmentRepository(session).save(assessment)
        session.flush()
        session.add(
            AssessmentAnswerRecord(
                assessment_id=assessment.id.value,
                question_id=999_999,
                position=0,
                score=10,
            )
        )

        with pytest.raises(IntegrityError):
            session.flush()
    finally:
        session.rollback()
        session.close()
        engine.dispose()
