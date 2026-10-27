"""Supplier Assessment application-flow tests."""

from datetime import UTC, datetime, timedelta

import pytest

from pysrmkit.adapters.clock.fixed import FixedClock
from pysrmkit.adapters.memory.assessment_repository import InMemorySupplierAssessmentRepository
from pysrmkit.adapters.memory.relationship_repository import (
    InMemorySupplierRelationshipRepository,
)
from pysrmkit.application.assessment.commands import (
    AssessmentQuestionInput,
    CompleteSupplierAssessment,
    CreateSupplierAssessment,
    RecordAssessmentAnswer,
)
from pysrmkit.application.assessment.handlers import (
    CompleteSupplierAssessmentHandler,
    CreateSupplierAssessmentHandler,
    RecordAssessmentAnswerHandler,
)
from pysrmkit.application.relationship.errors import SupplierRelationshipNotFound
from pysrmkit.domain.assessment.events import SupplierAssessmentCompleted
from pysrmkit.domain.assessment.value_objects import AssessmentDecision
from pysrmkit.domain.common.events import DomainEvent
from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId

CREATED_AT = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
COMPLETED_AT = CREATED_AT + timedelta(hours=1)


class RecordingEventDispatcher:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def dispatch(self, events: tuple[DomainEvent, ...]) -> None:
        self.events.extend(events)


def save_relationship(repository: InMemorySupplierRelationshipRepository) -> SupplierRelationshipId:
    relationship = SupplierRelationship.create(
        relationship_id=SupplierRelationshipId.new(),
        supplier_id=SupplierId.new(),
        organization_id=InternalOrganizationId("ORG-A"),
        occurred_at=CREATED_AT,
    )
    relationship.pull_events()
    repository.save(relationship)
    return relationship.id


def test_create_record_and_complete_assessment_through_handlers() -> None:
    relationships = InMemorySupplierRelationshipRepository()
    assessments = InMemorySupplierAssessmentRepository()
    relationship_id = save_relationship(relationships)
    created = CreateSupplierAssessmentHandler(
        assessment_repository=assessments,
        relationship_repository=relationships,
        clock=FixedClock(CREATED_AT),
    ).handle(
        CreateSupplierAssessment(
            relationship_id=relationship_id,
            assessment_type="questionnaire",
            questions=(
                AssessmentQuestionInput(code="LEGAL", maximum_score=50),
                AssessmentQuestionInput(code="QUALITY", maximum_score=50),
            ),
        )
    )

    record = RecordAssessmentAnswerHandler(repository=assessments)
    record.handle(
        RecordAssessmentAnswer(
            assessment_id=created.assessment_id,
            question_code="LEGAL",
            score=45,
        )
    )
    record.handle(
        RecordAssessmentAnswer(
            assessment_id=created.assessment_id,
            question_code="QUALITY",
            score=45,
        )
    )
    dispatcher = RecordingEventDispatcher()
    completed = CompleteSupplierAssessmentHandler(
        repository=assessments,
        clock=FixedClock(COMPLETED_AT),
        event_dispatcher=dispatcher,
    ).handle(
        CompleteSupplierAssessment(
            assessment_id=created.assessment_id,
            decision=AssessmentDecision.APPROVED,
        )
    )

    assert completed.score.value == 90
    loaded = assessments.get(created.assessment_id)
    assert loaded is not None
    assert loaded.created_at == CREATED_AT
    assert loaded.completed_at == COMPLETED_AT
    assert loaded.is_complete is True
    assert len(dispatcher.events) == 1
    assert isinstance(dispatcher.events[0], SupplierAssessmentCompleted)


def test_create_assessment_requires_existing_relationship() -> None:
    handler = CreateSupplierAssessmentHandler(
        assessment_repository=InMemorySupplierAssessmentRepository(),
        relationship_repository=InMemorySupplierRelationshipRepository(),
        clock=FixedClock(CREATED_AT),
    )

    with pytest.raises(SupplierRelationshipNotFound):
        handler.handle(
            CreateSupplierAssessment(
                relationship_id=SupplierRelationshipId.new(),
                assessment_type="QUESTIONNAIRE",
                questions=(AssessmentQuestionInput(code="LEGAL"),),
            )
        )
