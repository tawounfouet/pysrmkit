"""Handlers orchestrating Supplier Assessment use cases."""

from __future__ import annotations

from pysrmkit.application.assessment.commands import (
    CompleteSupplierAssessment,
    CreateSupplierAssessment,
    RecordAssessmentAnswer,
)
from pysrmkit.application.assessment.errors import SupplierAssessmentNotFound
from pysrmkit.application.assessment.results import (
    CompleteSupplierAssessmentResult,
    CreateSupplierAssessmentResult,
)
from pysrmkit.application.relationship.errors import SupplierRelationshipNotFound
from pysrmkit.domain.assessment.entities import SupplierAssessment
from pysrmkit.domain.assessment.value_objects import (
    AssessmentAnswer,
    AssessmentId,
    AssessmentQuestion,
    AssessmentType,
)
from pysrmkit.ports.clock import Clock
from pysrmkit.ports.events import DomainEventDispatcher
from pysrmkit.ports.repositories.assessment import SupplierAssessmentRepository
from pysrmkit.ports.repositories.relationship import SupplierRelationshipRepository


class _AssessmentLoader:
    def __init__(self, repository: SupplierAssessmentRepository) -> None:
        self._repository = repository

    def load(self, assessment_id: AssessmentId) -> SupplierAssessment:
        assessment = self._repository.get(assessment_id)
        if assessment is None:
            raise SupplierAssessmentNotFound(f"SupplierAssessment {assessment_id} does not exist")
        return assessment


class CreateSupplierAssessmentHandler:
    """Creates an assessment for an existing SupplierRelationship."""

    def __init__(
        self,
        *,
        assessment_repository: SupplierAssessmentRepository,
        relationship_repository: SupplierRelationshipRepository,
        clock: Clock,
    ) -> None:
        self._assessment_repository = assessment_repository
        self._relationship_repository = relationship_repository
        self._clock = clock

    def handle(self, command: CreateSupplierAssessment) -> CreateSupplierAssessmentResult:
        relationship = self._relationship_repository.get(command.relationship_id)
        if relationship is None:
            raise SupplierRelationshipNotFound(
                f"SupplierRelationship {command.relationship_id} does not exist"
            )

        assessment = SupplierAssessment.create(
            assessment_id=AssessmentId.new(),
            relationship_id=relationship.id,
            assessment_type=AssessmentType(command.assessment_type),
            created_at=self._clock.now(),
            questions=tuple(
                AssessmentQuestion(
                    code=item.code,
                    mandatory=item.mandatory,
                    maximum_score=item.maximum_score,
                )
                for item in command.questions
            ),
        )
        self._assessment_repository.save(assessment)
        return CreateSupplierAssessmentResult(assessment_id=assessment.id)


class RecordAssessmentAnswerHandler:
    """Records one answer through the SupplierAssessment Aggregate."""

    def __init__(self, *, repository: SupplierAssessmentRepository) -> None:
        self._repository = repository
        self._loader = _AssessmentLoader(repository)

    def handle(self, command: RecordAssessmentAnswer) -> None:
        assessment = self._loader.load(command.assessment_id)
        assessment.record_answer(
            AssessmentAnswer(
                question_code=command.question_code,
                score=command.score,
            )
        )
        self._repository.save(assessment)


class CompleteSupplierAssessmentHandler:
    """Completes a SupplierAssessment and dispatches its Domain Event."""

    def __init__(
        self,
        *,
        repository: SupplierAssessmentRepository,
        clock: Clock,
        event_dispatcher: DomainEventDispatcher,
    ) -> None:
        self._repository = repository
        self._clock = clock
        self._event_dispatcher = event_dispatcher
        self._loader = _AssessmentLoader(repository)

    def handle(self, command: CompleteSupplierAssessment) -> CompleteSupplierAssessmentResult:
        assessment = self._loader.load(command.assessment_id)
        assessment.complete(
            occurred_at=self._clock.now(),
            decision=command.decision,
        )
        score = assessment.score
        assert score is not None
        self._repository.save(assessment)
        self._event_dispatcher.dispatch(assessment.pull_events())
        return CompleteSupplierAssessmentResult(
            assessment_id=assessment.id,
            score=score,
        )
