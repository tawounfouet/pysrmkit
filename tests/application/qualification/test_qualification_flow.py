"""Supplier Qualification application-flow tests."""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

import pytest

from pysrmkit.adapters.clock.fixed import FixedClock
from pysrmkit.adapters.memory.assessment_repository import InMemorySupplierAssessmentRepository
from pysrmkit.adapters.memory.onboarding_repository import InMemorySupplierOnboardingRepository
from pysrmkit.adapters.memory.qualification_repository import (
    InMemorySupplierQualificationRepository,
)
from pysrmkit.adapters.memory.relationship_repository import (
    InMemorySupplierRelationshipRepository,
)
from pysrmkit.application.qualification.commands import (
    EvaluateSupplierQualification,
    RequestSupplierQualification,
)
from pysrmkit.application.qualification.errors import CurrentQualificationAlreadyExists
from pysrmkit.application.qualification.handlers import (
    EvaluateSupplierQualificationHandler,
    RequestSupplierQualificationHandler,
)
from pysrmkit.application.relationship.errors import SupplierRelationshipNotFound
from pysrmkit.domain.assessment.entities import SupplierAssessment
from pysrmkit.domain.assessment.value_objects import (
    AssessmentAnswer,
    AssessmentId,
    AssessmentQuestion,
    AssessmentType,
)
from pysrmkit.domain.common.events import DomainEvent
from pysrmkit.domain.onboarding.entities import SupplierOnboarding
from pysrmkit.domain.onboarding.value_objects import OnboardingId
from pysrmkit.domain.qualification.events import (
    SupplierQualificationRejected,
    SupplierQualificationRequested,
    SupplierQualified,
)
from pysrmkit.domain.qualification.policies import QualificationContext, QualificationPolicy
from pysrmkit.domain.qualification.value_objects import (
    QualificationDecision,
    QualificationScope,
    QualificationStatus,
)
from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierLifecycleStage,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import CategoryCode, SupplierId

REQUESTED_AT = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
EVALUATED_AT = REQUESTED_AT + timedelta(hours=1)


class RecordingEventDispatcher:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def dispatch(self, events: tuple[DomainEvent, ...]) -> None:
        self.events.extend(events)


def _qualification_context_list() -> list[QualificationContext]:
    return []


@dataclass(frozen=True, slots=True)
class RecordingQualificationPolicy(QualificationPolicy):
    contexts: list[QualificationContext] = field(
        default_factory=_qualification_context_list,
        compare=False,
    )

    def evaluate(
        self,
        context: QualificationContext,
        *,
        evaluated_at: datetime,
    ) -> QualificationDecision:
        self.contexts.append(context)
        return QualificationPolicy.evaluate(
            self,
            context,
            evaluated_at=evaluated_at,
        )


def save_relationship(repository: InMemorySupplierRelationshipRepository) -> SupplierRelationshipId:
    relationship = SupplierRelationship.reconstitute(
        relationship_id=SupplierRelationshipId.new(),
        supplier_id=SupplierId.new(),
        organization_id=InternalOrganizationId("ORG-A"),
        stage=SupplierLifecycleStage.ONBOARDING,
    )
    repository.save(relationship)
    return relationship.id


def save_completed_onboarding(
    repository: InMemorySupplierOnboardingRepository,
    relationship_id: SupplierRelationshipId,
) -> None:
    repository.save(
        SupplierOnboarding.reconstitute(
            onboarding_id=OnboardingId.new(),
            relationship_id=relationship_id,
            started_at=REQUESTED_AT,
            completed_at=REQUESTED_AT,
        )
    )


def save_completed_assessment(
    repository: InMemorySupplierAssessmentRepository,
    relationship_id: SupplierRelationshipId,
    *,
    score: int,
) -> None:
    assessment = SupplierAssessment.create(
        assessment_id=AssessmentId.new(),
        relationship_id=relationship_id,
        assessment_type=AssessmentType("QUESTIONNAIRE"),
        created_at=REQUESTED_AT,
        questions=(AssessmentQuestion(code="CORE", maximum_score=100),),
    )
    assessment.record_answer(AssessmentAnswer(question_code="CORE", score=score))
    assessment.complete(occurred_at=REQUESTED_AT)
    assessment.pull_events()
    repository.save(assessment)


def request_qualification(
    *,
    relationships: InMemorySupplierRelationshipRepository,
    qualifications: InMemorySupplierQualificationRepository,
    relationship_id: SupplierRelationshipId,
    scope: QualificationScope,
    dispatcher: RecordingEventDispatcher,
):
    return RequestSupplierQualificationHandler(
        relationship_repository=relationships,
        qualification_repository=qualifications,
        clock=FixedClock(REQUESTED_AT),
        event_dispatcher=dispatcher,
    ).handle(RequestSupplierQualification(relationship_id=relationship_id, scope=scope))


def test_request_handler_persists_pending_qualification_and_dispatches_event() -> None:
    relationships = InMemorySupplierRelationshipRepository()
    qualifications = InMemorySupplierQualificationRepository()
    dispatcher = RecordingEventDispatcher()
    relationship_id = save_relationship(relationships)
    scope = QualificationScope(category_code=CategoryCode("IT_SERVICES"))

    result = request_qualification(
        relationships=relationships,
        qualifications=qualifications,
        relationship_id=relationship_id,
        scope=scope,
        dispatcher=dispatcher,
    )

    loaded = qualifications.get(result.qualification_id)
    assert loaded is not None
    assert loaded.status is QualificationStatus.PENDING
    assert loaded.requested_at == REQUESTED_AT
    assert len(dispatcher.events) == 1
    assert isinstance(dispatcher.events[0], SupplierQualificationRequested)


def test_request_handler_rejects_duplicate_current_relationship_scope() -> None:
    relationships = InMemorySupplierRelationshipRepository()
    qualifications = InMemorySupplierQualificationRepository()
    dispatcher = RecordingEventDispatcher()
    relationship_id = save_relationship(relationships)
    scope = QualificationScope(category_code=CategoryCode("IT_SERVICES"))
    request_qualification(
        relationships=relationships,
        qualifications=qualifications,
        relationship_id=relationship_id,
        scope=scope,
        dispatcher=dispatcher,
    )
    dispatcher.events.clear()

    with pytest.raises(CurrentQualificationAlreadyExists):
        request_qualification(
            relationships=relationships,
            qualifications=qualifications,
            relationship_id=relationship_id,
            scope=scope,
            dispatcher=dispatcher,
        )

    assert dispatcher.events == []


def test_request_handler_requires_existing_relationship() -> None:
    handler = RequestSupplierQualificationHandler(
        relationship_repository=InMemorySupplierRelationshipRepository(),
        qualification_repository=InMemorySupplierQualificationRepository(),
        clock=FixedClock(REQUESTED_AT),
        event_dispatcher=RecordingEventDispatcher(),
    )

    with pytest.raises(SupplierRelationshipNotFound):
        handler.handle(
            RequestSupplierQualification(
                relationship_id=SupplierRelationshipId.new(),
                scope=QualificationScope(category_code=CategoryCode("IT_SERVICES")),
            )
        )


def test_evaluate_handler_invokes_policy_and_persists_qualified_decision() -> None:
    relationships = InMemorySupplierRelationshipRepository()
    qualifications = InMemorySupplierQualificationRepository()
    onboardings = InMemorySupplierOnboardingRepository()
    assessments = InMemorySupplierAssessmentRepository()
    dispatcher = RecordingEventDispatcher()
    relationship_id = save_relationship(relationships)
    save_completed_onboarding(onboardings, relationship_id)
    save_completed_assessment(assessments, relationship_id, score=90)
    requested = request_qualification(
        relationships=relationships,
        qualifications=qualifications,
        relationship_id=relationship_id,
        scope=QualificationScope(category_code=CategoryCode("IT_SERVICES")),
        dispatcher=dispatcher,
    )
    dispatcher.events.clear()
    policy = RecordingQualificationPolicy(minimum_assessment_score=80)
    handler = EvaluateSupplierQualificationHandler(
        qualification_repository=qualifications,
        assessment_repository=assessments,
        onboarding_repository=onboardings,
        policy=policy,
        clock=FixedClock(EVALUATED_AT),
        event_dispatcher=dispatcher,
    )

    result = handler.handle(
        EvaluateSupplierQualification(qualification_id=requested.qualification_id)
    )

    assert len(policy.contexts) == 1
    context = policy.contexts[0]
    assert context == QualificationContext(
        onboarding_complete=True,
        assessment_completed=True,
        assessment_score=90,
        required_answers_complete=True,
    )
    assert result.status is QualificationStatus.QUALIFIED
    assert result.decision.decided_at == EVALUATED_AT
    loaded = qualifications.get(requested.qualification_id)
    assert loaded is not None
    assert loaded.status is QualificationStatus.QUALIFIED
    assert len(dispatcher.events) == 1
    assert isinstance(dispatcher.events[0], SupplierQualified)


def test_evaluate_handler_dispatches_rejection_from_policy() -> None:
    relationships = InMemorySupplierRelationshipRepository()
    qualifications = InMemorySupplierQualificationRepository()
    onboardings = InMemorySupplierOnboardingRepository()
    assessments = InMemorySupplierAssessmentRepository()
    dispatcher = RecordingEventDispatcher()
    relationship_id = save_relationship(relationships)
    save_completed_onboarding(onboardings, relationship_id)
    save_completed_assessment(assessments, relationship_id, score=60)
    requested = request_qualification(
        relationships=relationships,
        qualifications=qualifications,
        relationship_id=relationship_id,
        scope=QualificationScope(category_code=CategoryCode("IT_SERVICES")),
        dispatcher=dispatcher,
    )
    dispatcher.events.clear()
    handler = EvaluateSupplierQualificationHandler(
        qualification_repository=qualifications,
        assessment_repository=assessments,
        onboarding_repository=onboardings,
        policy=QualificationPolicy(minimum_assessment_score=80),
        clock=FixedClock(EVALUATED_AT),
        event_dispatcher=dispatcher,
    )

    result = handler.handle(
        EvaluateSupplierQualification(qualification_id=requested.qualification_id)
    )

    assert result.status is QualificationStatus.NOT_QUALIFIED
    assert "ASSESSMENT_MINIMUM_SCORE" in result.decision.failed_requirements
    assert len(dispatcher.events) == 1
    assert isinstance(dispatcher.events[0], SupplierQualificationRejected)
