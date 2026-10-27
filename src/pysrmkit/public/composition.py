"""Runtime composition roots for the public PySRMKit API."""

from __future__ import annotations

from pysrmkit.adapters.clock.system import SystemClock
from pysrmkit.adapters.events.in_process import InProcessDomainEventDispatcher
from pysrmkit.adapters.memory.assessment_repository import InMemorySupplierAssessmentRepository
from pysrmkit.adapters.memory.onboarding_repository import InMemorySupplierOnboardingRepository
from pysrmkit.adapters.memory.qualification_repository import InMemorySupplierQualificationRepository
from pysrmkit.adapters.memory.relationship_repository import InMemorySupplierRelationshipRepository
from pysrmkit.adapters.memory.supplier_repository import InMemorySupplierRepository
from pysrmkit.adapters.memory.unit_of_work import InMemorySupplierOnboardingUnitOfWork
from pysrmkit.application.assessment.handlers import (
    CompleteSupplierAssessmentHandler,
    CreateSupplierAssessmentHandler,
    RecordAssessmentAnswerHandler,
)
from pysrmkit.application.onboarding.handlers import (
    CompleteSupplierOnboardingHandler,
    GetOnboardingProgressHandler,
    SatisfyOnboardingRequirementHandler,
)
from pysrmkit.application.qualification.handlers import (
    EvaluateSupplierQualificationHandler,
    RequestSupplierQualificationHandler,
)
from pysrmkit.application.relationship.handlers import (
    CreateSupplierRelationshipHandler,
    InviteSupplierRelationshipHandler,
    StartSupplierOnboardingHandler,
)
from pysrmkit.application.supplier.handlers import RegisterSupplierHandler
from pysrmkit.domain.qualification.policies import QualificationPolicy
from pysrmkit.public.capabilities import (
    AssessmentsAPI,
    OnboardingsAPI,
    QualificationsAPI,
    RelationshipsAPI,
    SuppliersAPI,
)
from pysrmkit.ports.clock import Clock
from pysrmkit.ports.events import DomainEventDispatcher


def compose_in_memory(
    *,
    clock: Clock | None = None,
    event_dispatcher: DomainEventDispatcher | None = None,
    qualification_policy: QualificationPolicy | None = None,
) -> tuple[
    SuppliersAPI,
    RelationshipsAPI,
    OnboardingsAPI,
    AssessmentsAPI,
    QualificationsAPI,
]:
    """Wire the complete local runtime using in-memory adapters.

    This function is the explicit Composition Root for the in-memory runtime.
    Dependencies are created once and shared by handlers that participate in the
    same runtime. Optional ports remain injectable for deterministic tests and
    host-application customization without introducing a DI container.
    """
    runtime_clock = clock or SystemClock()
    runtime_events = event_dispatcher or InProcessDomainEventDispatcher()
    runtime_policy = qualification_policy or QualificationPolicy()

    suppliers = InMemorySupplierRepository()
    relationships = InMemorySupplierRelationshipRepository()
    onboardings = InMemorySupplierOnboardingRepository()
    assessments = InMemorySupplierAssessmentRepository()
    qualifications = InMemorySupplierQualificationRepository()

    onboarding_uow = InMemorySupplierOnboardingUnitOfWork(
        relationship_repository=relationships,
        onboarding_repository=onboardings,
    )

    suppliers_api = SuppliersAPI(
        register_supplier=RegisterSupplierHandler(
            repository=suppliers,
            clock=runtime_clock,
            event_dispatcher=runtime_events,
        )
    )
    relationships_api = RelationshipsAPI(
        create_relationship=CreateSupplierRelationshipHandler(
            supplier_repository=suppliers,
            relationship_repository=relationships,
            clock=runtime_clock,
            event_dispatcher=runtime_events,
        ),
        invite_relationship=InviteSupplierRelationshipHandler(
            relationship_repository=relationships,
            clock=runtime_clock,
            event_dispatcher=runtime_events,
        ),
        start_onboarding=StartSupplierOnboardingHandler(
            unit_of_work=onboarding_uow,
            clock=runtime_clock,
            event_dispatcher=runtime_events,
        ),
    )
    onboardings_api = OnboardingsAPI(
        satisfy_requirement=SatisfyOnboardingRequirementHandler(repository=onboardings),
        complete_onboarding=CompleteSupplierOnboardingHandler(
            repository=onboardings,
            clock=runtime_clock,
            event_dispatcher=runtime_events,
        ),
        get_progress=GetOnboardingProgressHandler(repository=onboardings),
    )
    assessments_api = AssessmentsAPI(
        create_assessment=CreateSupplierAssessmentHandler(
            assessment_repository=assessments,
            relationship_repository=relationships,
            clock=runtime_clock,
        ),
        record_answer=RecordAssessmentAnswerHandler(repository=assessments),
        complete_assessment=CompleteSupplierAssessmentHandler(
            repository=assessments,
            clock=runtime_clock,
            event_dispatcher=runtime_events,
        ),
    )
    qualifications_api = QualificationsAPI(
        request_qualification=RequestSupplierQualificationHandler(
            relationship_repository=relationships,
            qualification_repository=qualifications,
            clock=runtime_clock,
            event_dispatcher=runtime_events,
        ),
        evaluate_qualification=EvaluateSupplierQualificationHandler(
            qualification_repository=qualifications,
            assessment_repository=assessments,
            onboarding_repository=onboardings,
            policy=runtime_policy,
            clock=runtime_clock,
            event_dispatcher=runtime_events,
        ),
    )

    return (
        suppliers_api,
        relationships_api,
        onboardings_api,
        assessments_api,
        qualifications_api,
    )
