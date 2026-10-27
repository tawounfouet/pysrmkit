"""Handlers orchestrating Supplier Qualification application use cases."""

from __future__ import annotations

from pysrmkit.application.qualification.commands import (
    EvaluateSupplierQualification,
    RequestSupplierQualification,
)
from pysrmkit.application.qualification.errors import (
    CurrentQualificationAlreadyExists,
    SupplierQualificationNotFound,
)
from pysrmkit.application.qualification.results import (
    EvaluateSupplierQualificationResult,
    RequestSupplierQualificationResult,
)
from pysrmkit.application.relationship.errors import SupplierRelationshipNotFound
from pysrmkit.domain.qualification.entities import SupplierQualification
from pysrmkit.domain.qualification.policies import QualificationContext, QualificationPolicy
from pysrmkit.domain.qualification.value_objects import QualificationId
from pysrmkit.ports.clock import Clock
from pysrmkit.ports.events import DomainEventDispatcher
from pysrmkit.ports.repositories.assessment import SupplierAssessmentRepository
from pysrmkit.ports.repositories.onboarding import SupplierOnboardingRepository
from pysrmkit.ports.repositories.qualification import SupplierQualificationRepository
from pysrmkit.ports.repositories.relationship import SupplierRelationshipRepository


class RequestSupplierQualificationHandler:
    """Creates a pending scoped qualification for an existing Relationship."""

    def __init__(
        self,
        *,
        relationship_repository: SupplierRelationshipRepository,
        qualification_repository: SupplierQualificationRepository,
        clock: Clock,
        event_dispatcher: DomainEventDispatcher,
    ) -> None:
        self._relationship_repository = relationship_repository
        self._qualification_repository = qualification_repository
        self._clock = clock
        self._event_dispatcher = event_dispatcher

    def handle(
        self,
        command: RequestSupplierQualification,
    ) -> RequestSupplierQualificationResult:
        relationship = self._relationship_repository.get(command.relationship_id)
        if relationship is None:
            raise SupplierRelationshipNotFound(
                f"SupplierRelationship {command.relationship_id} does not exist"
            )

        current = self._qualification_repository.find_current_for_scope(
            relationship.id,
            command.scope,
        )
        if current is not None:
            raise CurrentQualificationAlreadyExists(
                "Current qualification already exists for this Relationship and Scope"
            )

        qualification = SupplierQualification.request(
            qualification_id=QualificationId.new(),
            relationship_id=relationship.id,
            scope=command.scope,
            occurred_at=self._clock.now(),
        )
        self._qualification_repository.save(qualification)
        self._event_dispatcher.dispatch(qualification.pull_events())
        return RequestSupplierQualificationResult(qualification_id=qualification.id)


class EvaluateSupplierQualificationHandler:
    """Collects facts, delegates the business decision to the Policy, and persists it."""

    def __init__(
        self,
        *,
        qualification_repository: SupplierQualificationRepository,
        assessment_repository: SupplierAssessmentRepository,
        onboarding_repository: SupplierOnboardingRepository,
        policy: QualificationPolicy,
        clock: Clock,
        event_dispatcher: DomainEventDispatcher,
    ) -> None:
        self._qualification_repository = qualification_repository
        self._assessment_repository = assessment_repository
        self._onboarding_repository = onboarding_repository
        self._policy = policy
        self._clock = clock
        self._event_dispatcher = event_dispatcher

    def handle(
        self,
        command: EvaluateSupplierQualification,
    ) -> EvaluateSupplierQualificationResult:
        qualification = self._qualification_repository.get(command.qualification_id)
        if qualification is None:
            raise SupplierQualificationNotFound(
                f"SupplierQualification {command.qualification_id} does not exist"
            )

        onboarding = self._onboarding_repository.find_for_relationship(
            qualification.relationship_id
        )
        assessment = self._assessment_repository.find_latest_for_relationship(
            qualification.relationship_id
        )

        assessment_score = None
        assessment_completed = False
        required_answers_complete = False
        if assessment is not None:
            assessment_completed = assessment.is_complete
            required_answers_complete = assessment.required_answers_complete
            if assessment.score is not None:
                assessment_score = assessment.score.value

        context = QualificationContext(
            onboarding_complete=onboarding is not None and onboarding.is_complete,
            assessment_completed=assessment_completed,
            assessment_score=assessment_score,
            required_answers_complete=required_answers_complete,
        )
        decision = self._policy.evaluate(
            context,
            evaluated_at=self._clock.now(),
        )
        qualification.apply_decision(decision)
        self._qualification_repository.save(qualification)
        self._event_dispatcher.dispatch(qualification.pull_events())

        return EvaluateSupplierQualificationResult(
            qualification_id=qualification.id,
            status=qualification.status,
            decision=decision,
        )
