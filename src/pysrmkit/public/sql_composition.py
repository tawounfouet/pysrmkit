"""SQLAlchemy runtime composition root for the public PySRMKit API."""

from __future__ import annotations

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from pysrmkit.adapters.clock.system import SystemClock
from pysrmkit.adapters.events.in_process import InProcessDomainEventDispatcher
from pysrmkit.adapters.sqlalchemy.repositories.assessment import (
    SqlAlchemySupplierAssessmentRepository,
)
from pysrmkit.adapters.sqlalchemy.repositories.onboarding import (
    SqlAlchemySupplierOnboardingRepository,
)
from pysrmkit.adapters.sqlalchemy.repositories.qualification import (
    SqlAlchemySupplierQualificationRepository,
)
from pysrmkit.adapters.sqlalchemy.repositories.relationship import (
    SqlAlchemySupplierRelationshipRepository,
)
from pysrmkit.adapters.sqlalchemy.repositories.supplier import SqlAlchemySupplierRepository
from pysrmkit.adapters.sqlalchemy.session import create_session_factory
from pysrmkit.adapters.sqlalchemy.transactional_handler import SqlAlchemyTransactionalHandler
from pysrmkit.adapters.sqlalchemy.unit_of_work import SqlAlchemySupplierOnboardingUnitOfWork
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
from pysrmkit.ports.clock import Clock
from pysrmkit.ports.events import DomainEventDispatcher
from pysrmkit.public.capabilities import (
    AssessmentsAPI,
    OnboardingsAPI,
    QualificationsAPI,
    RelationshipsAPI,
    SuppliersAPI,
)


def compose_sql(
    engine: Engine,
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
    """Wire the public runtime to SQLAlchemy with operation-scoped transactions."""
    runtime_clock = clock or SystemClock()
    runtime_events = event_dispatcher or InProcessDomainEventDispatcher()
    runtime_policy = qualification_policy or QualificationPolicy()
    sessions = create_session_factory(engine)

    def supplier_repository(session: Session) -> SqlAlchemySupplierRepository:
        return SqlAlchemySupplierRepository(session)

    def relationship_repository(session: Session) -> SqlAlchemySupplierRelationshipRepository:
        return SqlAlchemySupplierRelationshipRepository(session)

    def onboarding_repository(session: Session) -> SqlAlchemySupplierOnboardingRepository:
        return SqlAlchemySupplierOnboardingRepository(session)

    def assessment_repository(session: Session) -> SqlAlchemySupplierAssessmentRepository:
        return SqlAlchemySupplierAssessmentRepository(session)

    def qualification_repository(session: Session) -> SqlAlchemySupplierQualificationRepository:
        return SqlAlchemySupplierQualificationRepository(session)

    suppliers_api = SuppliersAPI(
        register_supplier=SqlAlchemyTransactionalHandler(
            session_factory=sessions,
            handler_factory=lambda session: RegisterSupplierHandler(
                repository=supplier_repository(session),
                clock=runtime_clock,
                event_dispatcher=runtime_events,
            ),
        )
    )
    relationships_api = RelationshipsAPI(
        create_relationship=SqlAlchemyTransactionalHandler(
            session_factory=sessions,
            handler_factory=lambda session: CreateSupplierRelationshipHandler(
                supplier_repository=supplier_repository(session),
                relationship_repository=relationship_repository(session),
                clock=runtime_clock,
                event_dispatcher=runtime_events,
            ),
        ),
        invite_relationship=SqlAlchemyTransactionalHandler(
            session_factory=sessions,
            handler_factory=lambda session: InviteSupplierRelationshipHandler(
                relationship_repository=relationship_repository(session),
                clock=runtime_clock,
                event_dispatcher=runtime_events,
            ),
        ),
        start_onboarding=StartSupplierOnboardingHandler(
            unit_of_work=SqlAlchemySupplierOnboardingUnitOfWork(sessions),
            clock=runtime_clock,
            event_dispatcher=runtime_events,
        ),
    )
    onboardings_api = OnboardingsAPI(
        satisfy_requirement=SqlAlchemyTransactionalHandler(
            session_factory=sessions,
            handler_factory=lambda session: SatisfyOnboardingRequirementHandler(
                repository=onboarding_repository(session)
            ),
        ),
        complete_onboarding=SqlAlchemyTransactionalHandler(
            session_factory=sessions,
            handler_factory=lambda session: CompleteSupplierOnboardingHandler(
                repository=onboarding_repository(session),
                clock=runtime_clock,
                event_dispatcher=runtime_events,
            ),
        ),
        get_progress=SqlAlchemyTransactionalHandler(
            session_factory=sessions,
            handler_factory=lambda session: GetOnboardingProgressHandler(
                repository=onboarding_repository(session)
            ),
        ),
    )
    assessments_api = AssessmentsAPI(
        create_assessment=SqlAlchemyTransactionalHandler(
            session_factory=sessions,
            handler_factory=lambda session: CreateSupplierAssessmentHandler(
                assessment_repository=assessment_repository(session),
                relationship_repository=relationship_repository(session),
                clock=runtime_clock,
            ),
        ),
        record_answer=SqlAlchemyTransactionalHandler(
            session_factory=sessions,
            handler_factory=lambda session: RecordAssessmentAnswerHandler(
                repository=assessment_repository(session)
            ),
        ),
        complete_assessment=SqlAlchemyTransactionalHandler(
            session_factory=sessions,
            handler_factory=lambda session: CompleteSupplierAssessmentHandler(
                repository=assessment_repository(session),
                clock=runtime_clock,
                event_dispatcher=runtime_events,
            ),
        ),
    )
    qualifications_api = QualificationsAPI(
        request_qualification=SqlAlchemyTransactionalHandler(
            session_factory=sessions,
            handler_factory=lambda session: RequestSupplierQualificationHandler(
                relationship_repository=relationship_repository(session),
                qualification_repository=qualification_repository(session),
                clock=runtime_clock,
                event_dispatcher=runtime_events,
            ),
        ),
        evaluate_qualification=SqlAlchemyTransactionalHandler(
            session_factory=sessions,
            handler_factory=lambda session: EvaluateSupplierQualificationHandler(
                qualification_repository=qualification_repository(session),
                assessment_repository=assessment_repository(session),
                onboarding_repository=onboarding_repository(session),
                policy=runtime_policy,
                clock=runtime_clock,
                event_dispatcher=runtime_events,
            ),
        ),
    )

    return (
        suppliers_api,
        relationships_api,
        onboardings_api,
        assessments_api,
        qualifications_api,
    )
