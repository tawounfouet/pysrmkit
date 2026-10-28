"""SQLAlchemy runtime composition root for the public PySRMKit API."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

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
from pysrmkit.public._handler import Handler
from pysrmkit.public._sql_boundary import SqlAlchemyErrorBoundaryHandler
from pysrmkit.public.capabilities import (
    AssessmentsAPI,
    OnboardingsAPI,
    QualificationsAPI,
    RelationshipsAPI,
    SuppliersAPI,
)
from pysrmkit.public.events import EventsAPI
from pysrmkit.public.query_handlers import (
    GetAssessmentHandler,
    GetCurrentQualificationForScopeHandler,
    GetOnboardingForRelationshipHandler,
    GetQualificationHandler,
    GetSupplierHandler,
    GetSupplierRelationshipHandler,
    ListSuppliersHandler,
)

_CommandT = TypeVar("_CommandT")
_ResultT = TypeVar("_ResultT")


def _transactional(
    sessions: Callable[[], Session],
    handler_factory: Callable[[Session], Handler[_CommandT, _ResultT]],
) -> Handler[_CommandT, _ResultT]:
    """Wrap one session-scoped handler with transaction and persistence boundaries."""
    return SqlAlchemyErrorBoundaryHandler(
        SqlAlchemyTransactionalHandler(
            session_factory=sessions,
            handler_factory=handler_factory,
        )
    )


def _transactional_events(
    sessions: Callable[[], Session],
    event_dispatcher: DomainEventDispatcher,
    handler_factory: Callable[
        [Session, DomainEventDispatcher],
        Handler[_CommandT, _ResultT],
    ],
) -> Handler[_CommandT, _ResultT]:
    """Publish events only after the surrounding SQL transaction commits."""
    return SqlAlchemyErrorBoundaryHandler(
        SqlAlchemyTransactionalHandler(
            session_factory=sessions,
            event_dispatcher=event_dispatcher,
            event_handler_factory=handler_factory,
        )
    )


def _guard(handler: Handler[_CommandT, _ResultT]) -> Handler[_CommandT, _ResultT]:
    """Apply only the persistence exception boundary to an existing transactional handler."""
    return SqlAlchemyErrorBoundaryHandler(handler)


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
    EventsAPI,
]:
    """Wire the public runtime to SQLAlchemy with operation-scoped transactions."""
    runtime_clock = clock or SystemClock()
    public_events = InProcessDomainEventDispatcher()
    runtime_events = event_dispatcher or public_events
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
        register_supplier=_transactional_events(
            sessions,
            runtime_events,
            lambda session, events: RegisterSupplierHandler(
                repository=supplier_repository(session),
                clock=runtime_clock,
                event_dispatcher=events,
            ),
        ),
        get_supplier=_transactional(
            sessions,
            lambda session: GetSupplierHandler(supplier_repository(session)),
        ),
        list_suppliers=_transactional(
            sessions,
            lambda session: ListSuppliersHandler(supplier_repository(session)),
        ),
    )
    relationships_api = RelationshipsAPI(
        create_relationship=_transactional_events(
            sessions,
            runtime_events,
            lambda session, events: CreateSupplierRelationshipHandler(
                supplier_repository=supplier_repository(session),
                relationship_repository=relationship_repository(session),
                clock=runtime_clock,
                event_dispatcher=events,
            ),
        ),
        invite_relationship=_transactional_events(
            sessions,
            runtime_events,
            lambda session, events: InviteSupplierRelationshipHandler(
                relationship_repository=relationship_repository(session),
                clock=runtime_clock,
                event_dispatcher=events,
            ),
        ),
        start_onboarding=_guard(
            StartSupplierOnboardingHandler(
                unit_of_work=SqlAlchemySupplierOnboardingUnitOfWork(sessions),
                clock=runtime_clock,
                event_dispatcher=runtime_events,
            )
        ),
        get_relationship=_transactional(
            sessions,
            lambda session: GetSupplierRelationshipHandler(relationship_repository(session)),
        ),
    )
    onboardings_api = OnboardingsAPI(
        satisfy_requirement=_transactional(
            sessions,
            lambda session: SatisfyOnboardingRequirementHandler(
                repository=onboarding_repository(session)
            ),
        ),
        complete_onboarding=_transactional_events(
            sessions,
            runtime_events,
            lambda session, events: CompleteSupplierOnboardingHandler(
                repository=onboarding_repository(session),
                clock=runtime_clock,
                event_dispatcher=events,
            ),
        ),
        get_progress=_transactional(
            sessions,
            lambda session: GetOnboardingProgressHandler(repository=onboarding_repository(session)),
        ),
        get_for_relationship=_transactional(
            sessions,
            lambda session: GetOnboardingForRelationshipHandler(onboarding_repository(session)),
        ),
    )
    assessments_api = AssessmentsAPI(
        create_assessment=_transactional(
            sessions,
            lambda session: CreateSupplierAssessmentHandler(
                assessment_repository=assessment_repository(session),
                relationship_repository=relationship_repository(session),
                clock=runtime_clock,
            ),
        ),
        record_answer=_transactional(
            sessions,
            lambda session: RecordAssessmentAnswerHandler(
                repository=assessment_repository(session)
            ),
        ),
        complete_assessment=_transactional_events(
            sessions,
            runtime_events,
            lambda session, events: CompleteSupplierAssessmentHandler(
                repository=assessment_repository(session),
                clock=runtime_clock,
                event_dispatcher=events,
            ),
        ),
        get_assessment=_transactional(
            sessions,
            lambda session: GetAssessmentHandler(assessment_repository(session)),
        ),
    )
    qualifications_api = QualificationsAPI(
        request_qualification=_transactional_events(
            sessions,
            runtime_events,
            lambda session, events: RequestSupplierQualificationHandler(
                relationship_repository=relationship_repository(session),
                qualification_repository=qualification_repository(session),
                clock=runtime_clock,
                event_dispatcher=events,
            ),
        ),
        evaluate_qualification=_transactional_events(
            sessions,
            runtime_events,
            lambda session, events: EvaluateSupplierQualificationHandler(
                qualification_repository=qualification_repository(session),
                assessment_repository=assessment_repository(session),
                onboarding_repository=onboarding_repository(session),
                policy=runtime_policy,
                clock=runtime_clock,
                event_dispatcher=events,
            ),
        ),
        get_qualification=_transactional(
            sessions,
            lambda session: GetQualificationHandler(qualification_repository(session)),
        ),
        get_current_for_scope=_transactional(
            sessions,
            lambda session: GetCurrentQualificationForScopeHandler(
                qualification_repository(session)
            ),
        ),
    )

    return (
        suppliers_api,
        relationships_api,
        onboardings_api,
        assessments_api,
        qualifications_api,
        EventsAPI(public_events),
    )
