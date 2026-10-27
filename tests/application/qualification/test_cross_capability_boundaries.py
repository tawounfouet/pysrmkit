"""Cross-capability coordination tests for the first qualification flow."""

from datetime import UTC, datetime

from pysrmkit.adapters.clock.fixed import FixedClock
from pysrmkit.adapters.memory.assessment_repository import InMemorySupplierAssessmentRepository
from pysrmkit.adapters.memory.onboarding_repository import InMemorySupplierOnboardingRepository
from pysrmkit.adapters.memory.qualification_repository import (
    InMemorySupplierQualificationRepository,
)
from pysrmkit.adapters.memory.relationship_repository import (
    InMemorySupplierRelationshipRepository,
)
from pysrmkit.application.qualification.commands import EvaluateSupplierQualification
from pysrmkit.application.qualification.handlers import EvaluateSupplierQualificationHandler
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
from pysrmkit.domain.qualification.entities import SupplierQualification
from pysrmkit.domain.qualification.policies import QualificationPolicy
from pysrmkit.domain.qualification.value_objects import (
    QualificationId,
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

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


class RecordingEventDispatcher:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def dispatch(self, events: tuple[DomainEvent, ...]) -> None:
        self.events.extend(events)


def test_completing_assessment_does_not_create_or_mutate_qualification() -> None:
    relationship_id = SupplierRelationshipId.new()
    assessment = SupplierAssessment.create(
        assessment_id=AssessmentId.new(),
        relationship_id=relationship_id,
        assessment_type=AssessmentType("QUESTIONNAIRE"),
        created_at=NOW,
        questions=(AssessmentQuestion(code="CORE"),),
    )
    assessment.record_answer(AssessmentAnswer(question_code="CORE", score=90))

    assessment.complete(occurred_at=NOW)

    assert assessment.is_complete is True
    assert assessment.score is not None


def test_qualification_evaluation_does_not_mutate_relationship_lifecycle() -> None:
    relationships = InMemorySupplierRelationshipRepository()
    relationship = SupplierRelationship.reconstitute(
        relationship_id=SupplierRelationshipId.new(),
        supplier_id=SupplierId.new(),
        organization_id=InternalOrganizationId("ORG-A"),
        stage=SupplierLifecycleStage.ONBOARDING,
    )
    relationships.save(relationship)

    onboardings = InMemorySupplierOnboardingRepository()
    onboardings.save(
        SupplierOnboarding.reconstitute(
            onboarding_id=OnboardingId.new(),
            relationship_id=relationship.id,
            started_at=NOW,
            completed_at=NOW,
        )
    )
    assessments = InMemorySupplierAssessmentRepository()
    assessment = SupplierAssessment.create(
        assessment_id=AssessmentId.new(),
        relationship_id=relationship.id,
        assessment_type=AssessmentType("QUESTIONNAIRE"),
        created_at=NOW,
        questions=(AssessmentQuestion(code="CORE"),),
    )
    assessment.record_answer(AssessmentAnswer(question_code="CORE", score=90))
    assessment.complete(occurred_at=NOW)
    assessment.pull_events()
    assessments.save(assessment)

    qualifications = InMemorySupplierQualificationRepository()
    qualification = SupplierQualification.request(
        qualification_id=QualificationId.new(),
        relationship_id=relationship.id,
        scope=QualificationScope(category_code=CategoryCode("IT_SERVICES")),
        occurred_at=NOW,
    )
    qualification.pull_events()
    qualifications.save(qualification)

    EvaluateSupplierQualificationHandler(
        qualification_repository=qualifications,
        assessment_repository=assessments,
        onboarding_repository=onboardings,
        policy=QualificationPolicy(minimum_assessment_score=80),
        clock=FixedClock(NOW),
        event_dispatcher=RecordingEventDispatcher(),
    ).handle(EvaluateSupplierQualification(qualification_id=qualification.id))

    persisted_relationship = relationships.get(relationship.id)
    persisted_qualification = qualifications.get(qualification.id)
    assert persisted_relationship is not None
    assert persisted_qualification is not None
    assert persisted_relationship.stage is SupplierLifecycleStage.ONBOARDING
    assert persisted_qualification.status is QualificationStatus.QUALIFIED
