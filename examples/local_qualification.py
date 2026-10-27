"""End-to-end local Supplier qualification using only PySRMKit Core adapters."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from pysrmkit.adapters.clock.fixed import FixedClock
from pysrmkit.adapters.events.in_process import InProcessDomainEventDispatcher
from pysrmkit.adapters.memory.assessment_repository import InMemorySupplierAssessmentRepository
from pysrmkit.adapters.memory.onboarding_repository import InMemorySupplierOnboardingRepository
from pysrmkit.adapters.memory.qualification_repository import (
    InMemorySupplierQualificationRepository,
)
from pysrmkit.adapters.memory.relationship_repository import (
    InMemorySupplierRelationshipRepository,
)
from pysrmkit.adapters.memory.supplier_repository import InMemorySupplierRepository
from pysrmkit.adapters.memory.unit_of_work import InMemorySupplierOnboardingUnitOfWork
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
from pysrmkit.application.onboarding.commands import (
    CompleteSupplierOnboarding,
    OnboardingRequirementInput,
    SatisfyOnboardingRequirement,
)
from pysrmkit.application.onboarding.handlers import (
    CompleteSupplierOnboardingHandler,
    SatisfyOnboardingRequirementHandler,
)
from pysrmkit.application.qualification.commands import (
    EvaluateSupplierQualification,
    RequestSupplierQualification,
)
from pysrmkit.application.qualification.handlers import (
    EvaluateSupplierQualificationHandler,
    RequestSupplierQualificationHandler,
)
from pysrmkit.application.relationship.commands import (
    CreateSupplierRelationship,
    InviteSupplierRelationship,
    StartSupplierOnboarding,
)
from pysrmkit.application.relationship.handlers import (
    CreateSupplierRelationshipHandler,
    InviteSupplierRelationshipHandler,
    StartSupplierOnboardingHandler,
)
from pysrmkit.application.supplier.commands import (
    ExternalIdentifierInput,
    RegisterSupplier,
)
from pysrmkit.application.supplier.handlers import RegisterSupplierHandler
from pysrmkit.domain.assessment.events import SupplierAssessmentCompleted
from pysrmkit.domain.common.events import DomainEvent
from pysrmkit.domain.onboarding.events import SupplierOnboardingCompleted
from pysrmkit.domain.onboarding.value_objects import OnboardingRequirementCode
from pysrmkit.domain.qualification.events import (
    SupplierQualificationRejected,
    SupplierQualificationRequested,
    SupplierQualified,
)
from pysrmkit.domain.qualification.policies import QualificationPolicy
from pysrmkit.domain.qualification.value_objects import (
    QualificationDecision,
    QualificationScope,
    QualificationStatus,
)
from pysrmkit.domain.relationship.events import (
    SupplierInvited,
    SupplierOnboardingStarted,
    SupplierRelationshipCreated,
)
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierLifecycleStage,
)
from pysrmkit.domain.supplier.events import SupplierCreated
from pysrmkit.domain.supplier.value_objects import CategoryCode

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class LocalQualificationOutcome:
    """Observable final state of the local Core qualification scenario."""

    supplier_exists: bool
    relationship_exists: bool
    relationship_stage: SupplierLifecycleStage
    onboarding_complete: bool
    assessment_complete: bool
    assessment_score: int
    qualification_scope: QualificationScope
    qualification_status: QualificationStatus
    qualification_decision: QualificationDecision
    observed_events: tuple[str, ...]


def _event_types() -> tuple[type[object], ...]:
    return (
        SupplierCreated,
        SupplierRelationshipCreated,
        SupplierInvited,
        SupplierOnboardingStarted,
        SupplierOnboardingCompleted,
        SupplierAssessmentCompleted,
        SupplierQualificationRequested,
        SupplierQualified,
        SupplierQualificationRejected,
    )


def run_local_qualification(*, assessment_score: int = 90) -> LocalQualificationOutcome:
    """Execute the complete local qualification path without network or database."""

    suppliers = InMemorySupplierRepository()
    relationships = InMemorySupplierRelationshipRepository()
    onboardings = InMemorySupplierOnboardingRepository()
    assessments = InMemorySupplierAssessmentRepository()
    qualifications = InMemorySupplierQualificationRepository()
    clock = FixedClock(NOW)
    dispatcher = InProcessDomainEventDispatcher()
    observed_events: list[str] = []

    def record_event(event: DomainEvent) -> None:
        observed_events.append(type(event).__name__)

    for event_type in _event_types():
        dispatcher.register(event_type, record_event)

    supplier = RegisterSupplierHandler(
        repository=suppliers,
        clock=clock,
        event_dispatcher=dispatcher,
    ).handle(
        RegisterSupplier(
            legal_name="Northwind Industrial SAS",
            trading_name="Northwind",
            supplier_type="LEGAL_ENTITY",
            country_code="FR",
            external_identifiers=(
                ExternalIdentifierInput(
                    kind="LOCAL_VENDOR_CODE",
                    value="NW-001",
                    source_system="LOCAL_EXAMPLE",
                ),
            ),
        )
    )

    organization_id = InternalOrganizationId("ORG-PARIS")
    relationship = CreateSupplierRelationshipHandler(
        supplier_repository=suppliers,
        relationship_repository=relationships,
        clock=clock,
        event_dispatcher=dispatcher,
    ).handle(
        CreateSupplierRelationship(
            supplier_id=supplier.supplier_id,
            organization_id=organization_id,
        )
    )

    InviteSupplierRelationshipHandler(
        relationship_repository=relationships,
        clock=clock,
        event_dispatcher=dispatcher,
    ).handle(InviteSupplierRelationship(relationship_id=relationship.relationship_id))

    StartSupplierOnboardingHandler(
        unit_of_work=InMemorySupplierOnboardingUnitOfWork(
            relationship_repository=relationships,
            onboarding_repository=onboardings,
        ),
        clock=clock,
        event_dispatcher=dispatcher,
    ).handle(
        StartSupplierOnboarding(
            relationship_id=relationship.relationship_id,
            requirements=(
                OnboardingRequirementInput(code="LEGAL_NAME"),
                OnboardingRequirementInput(code="BANK_REFERENCE", mandatory=False),
            ),
        )
    )

    onboarding = onboardings.find_for_relationship(relationship.relationship_id)
    assert onboarding is not None
    SatisfyOnboardingRequirementHandler(repository=onboardings).handle(
        SatisfyOnboardingRequirement(
            onboarding_id=onboarding.id,
            requirement_code=OnboardingRequirementCode("LEGAL_NAME"),
        )
    )
    CompleteSupplierOnboardingHandler(
        repository=onboardings,
        clock=clock,
        event_dispatcher=dispatcher,
    ).handle(CompleteSupplierOnboarding(onboarding_id=onboarding.id))

    assessment = CreateSupplierAssessmentHandler(
        assessment_repository=assessments,
        relationship_repository=relationships,
        clock=clock,
    ).handle(
        CreateSupplierAssessment(
            relationship_id=relationship.relationship_id,
            assessment_type="QUESTIONNAIRE",
            questions=(
                AssessmentQuestionInput(
                    code="CORE_READINESS",
                    maximum_score=100,
                ),
            ),
        )
    )
    RecordAssessmentAnswerHandler(repository=assessments).handle(
        RecordAssessmentAnswer(
            assessment_id=assessment.assessment_id,
            question_code="CORE_READINESS",
            score=assessment_score,
        )
    )
    CompleteSupplierAssessmentHandler(
        repository=assessments,
        clock=clock,
        event_dispatcher=dispatcher,
    ).handle(CompleteSupplierAssessment(assessment_id=assessment.assessment_id))

    scope = QualificationScope(
        organization_id=organization_id,
        category_code=CategoryCode("IT_SERVICES"),
    )
    qualification = RequestSupplierQualificationHandler(
        relationship_repository=relationships,
        qualification_repository=qualifications,
        clock=clock,
        event_dispatcher=dispatcher,
    ).handle(
        RequestSupplierQualification(
            relationship_id=relationship.relationship_id,
            scope=scope,
        )
    )
    EvaluateSupplierQualificationHandler(
        qualification_repository=qualifications,
        assessment_repository=assessments,
        onboarding_repository=onboardings,
        policy=QualificationPolicy(minimum_assessment_score=80),
        clock=clock,
        event_dispatcher=dispatcher,
    ).handle(
        EvaluateSupplierQualification(
            qualification_id=qualification.qualification_id,
        )
    )

    persisted_supplier = suppliers.get(supplier.supplier_id)
    persisted_relationship = relationships.get(relationship.relationship_id)
    persisted_onboarding = onboardings.find_for_relationship(relationship.relationship_id)
    persisted_assessment = assessments.get(assessment.assessment_id)
    persisted_qualification = qualifications.get(qualification.qualification_id)

    assert persisted_relationship is not None
    assert persisted_onboarding is not None
    assert persisted_assessment is not None
    assert persisted_assessment.score is not None
    assert persisted_qualification is not None
    assert persisted_qualification.decision is not None

    return LocalQualificationOutcome(
        supplier_exists=persisted_supplier is not None,
        relationship_exists=True,
        relationship_stage=persisted_relationship.stage,
        onboarding_complete=persisted_onboarding.is_complete,
        assessment_complete=persisted_assessment.is_complete,
        assessment_score=persisted_assessment.score.value,
        qualification_scope=persisted_qualification.scope,
        qualification_status=persisted_qualification.status,
        qualification_decision=persisted_qualification.decision,
        observed_events=tuple(observed_events),
    )


def main() -> None:
    """Run the successful local scenario and print its pedagogical event trace."""

    outcome = run_local_qualification()
    for event_name in outcome.observed_events:
        print(f"[EVENT] {event_name}")
    print(f"[RESULT] Qualification status: {outcome.qualification_status}")


if __name__ == "__main__":
    main()
