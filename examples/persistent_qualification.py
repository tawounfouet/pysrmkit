"""Persistent end-to-end Supplier qualification with SQLAlchemy and Alembic."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from alembic import command
from alembic.config import Config
from sqlalchemy.orm import Session

from pysrmkit.adapters.clock.fixed import FixedClock
from pysrmkit.adapters.events.deferred import DeferredDomainEventDispatcher
from pysrmkit.adapters.events.in_process import InProcessDomainEventDispatcher
from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
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
from pysrmkit.adapters.sqlalchemy.unit_of_work import SqlAlchemySupplierOnboardingUnitOfWork
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
from pysrmkit.application.supplier.commands import ExternalIdentifierInput, RegisterSupplier
from pysrmkit.application.supplier.handlers import RegisterSupplierHandler
from pysrmkit.domain.assessment.events import SupplierAssessmentCompleted
from pysrmkit.domain.assessment.value_objects import AssessmentId
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
    QualificationId,
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
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.events import SupplierCreated
from pysrmkit.domain.supplier.value_objects import CategoryCode, SupplierId

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, slots=True)
class PersistentQualificationOutcome:
    """Business state reloaded through a completely new persistence context."""

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


def _upgrade_database(database_url: str) -> None:
    config = Config(str(_REPOSITORY_ROOT / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    command.upgrade(config, "head")


def _commit_and_publish(
    session: Session,
    dispatcher: DeferredDomainEventDispatcher,
) -> None:
    try:
        session.commit()
    except Exception:
        session.rollback()
        dispatcher.discard()
        raise
    dispatcher.publish()


def run_persistent_qualification(
    database_url: str,
    *,
    assessment_score: int = 90,
) -> PersistentQualificationOutcome:
    """Execute, commit, destroy, recreate, and reload the qualification journey."""

    _upgrade_database(database_url)
    engine = create_persistence_engine(database_url)
    session_factory = create_session_factory(engine)
    clock = FixedClock(NOW)
    downstream = InProcessDomainEventDispatcher()
    dispatcher = DeferredDomainEventDispatcher(downstream)
    observed_events: list[str] = []

    def record_event(event: DomainEvent) -> None:
        observed_events.append(type(event).__name__)

    for event_type in _event_types():
        downstream.register(event_type, record_event)

    supplier_id: SupplierId
    relationship_id: SupplierRelationshipId
    assessment_id: AssessmentId
    qualification_id: QualificationId

    try:
        with session_factory() as session:
            suppliers = SqlAlchemySupplierRepository(session)
            relationships = SqlAlchemySupplierRelationshipRepository(session)
            onboardings = SqlAlchemySupplierOnboardingRepository(session)
            assessments = SqlAlchemySupplierAssessmentRepository(session)
            qualifications = SqlAlchemySupplierQualificationRepository(session)

            supplier_result = RegisterSupplierHandler(
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
                            value="NW-PERSIST-001",
                            source_system="PERSISTENT_EXAMPLE",
                        ),
                    ),
                )
            )
            supplier_id = supplier_result.supplier_id
            _commit_and_publish(session, dispatcher)

            organization_id = InternalOrganizationId("ORG-PARIS")
            relationship_result = CreateSupplierRelationshipHandler(
                supplier_repository=suppliers,
                relationship_repository=relationships,
                clock=clock,
                event_dispatcher=dispatcher,
            ).handle(
                CreateSupplierRelationship(
                    supplier_id=supplier_id,
                    organization_id=organization_id,
                )
            )
            relationship_id = relationship_result.relationship_id
            _commit_and_publish(session, dispatcher)

            InviteSupplierRelationshipHandler(
                relationship_repository=relationships,
                clock=clock,
                event_dispatcher=dispatcher,
            ).handle(InviteSupplierRelationship(relationship_id=relationship_id))
            _commit_and_publish(session, dispatcher)

            StartSupplierOnboardingHandler(
                unit_of_work=SqlAlchemySupplierOnboardingUnitOfWork(session_factory),
                clock=clock,
                event_dispatcher=dispatcher,
            ).handle(
                StartSupplierOnboarding(
                    relationship_id=relationship_id,
                    requirements=(
                        OnboardingRequirementInput(code="LEGAL_NAME"),
                        OnboardingRequirementInput(code="BANK_REFERENCE", mandatory=False),
                    ),
                )
            )
            dispatcher.publish()
            session.expire_all()

            onboarding = onboardings.find_for_relationship(relationship_id)
            assert onboarding is not None

            SatisfyOnboardingRequirementHandler(repository=onboardings).handle(
                SatisfyOnboardingRequirement(
                    onboarding_id=onboarding.id,
                    requirement_code=OnboardingRequirementCode("LEGAL_NAME"),
                )
            )
            _commit_and_publish(session, dispatcher)

            CompleteSupplierOnboardingHandler(
                repository=onboardings,
                clock=clock,
                event_dispatcher=dispatcher,
            ).handle(CompleteSupplierOnboarding(onboarding_id=onboarding.id))
            _commit_and_publish(session, dispatcher)

            assessment_result = CreateSupplierAssessmentHandler(
                assessment_repository=assessments,
                relationship_repository=relationships,
                clock=clock,
            ).handle(
                CreateSupplierAssessment(
                    relationship_id=relationship_id,
                    assessment_type="QUESTIONNAIRE",
                    questions=(
                        AssessmentQuestionInput(
                            code="CORE_READINESS",
                            maximum_score=100,
                        ),
                    ),
                )
            )
            assessment_id = assessment_result.assessment_id
            _commit_and_publish(session, dispatcher)

            RecordAssessmentAnswerHandler(repository=assessments).handle(
                RecordAssessmentAnswer(
                    assessment_id=assessment_id,
                    question_code="CORE_READINESS",
                    score=assessment_score,
                )
            )
            _commit_and_publish(session, dispatcher)

            CompleteSupplierAssessmentHandler(
                repository=assessments,
                clock=clock,
                event_dispatcher=dispatcher,
            ).handle(CompleteSupplierAssessment(assessment_id=assessment_id))
            _commit_and_publish(session, dispatcher)

            scope = QualificationScope(
                organization_id=organization_id,
                category_code=CategoryCode("IT_SERVICES"),
            )
            qualification_result = RequestSupplierQualificationHandler(
                relationship_repository=relationships,
                qualification_repository=qualifications,
                clock=clock,
                event_dispatcher=dispatcher,
            ).handle(
                RequestSupplierQualification(
                    relationship_id=relationship_id,
                    scope=scope,
                )
            )
            qualification_id = qualification_result.qualification_id
            _commit_and_publish(session, dispatcher)

            EvaluateSupplierQualificationHandler(
                qualification_repository=qualifications,
                assessment_repository=assessments,
                onboarding_repository=onboardings,
                policy=QualificationPolicy(minimum_assessment_score=80),
                clock=clock,
                event_dispatcher=dispatcher,
            ).handle(EvaluateSupplierQualification(qualification_id=qualification_id))
            _commit_and_publish(session, dispatcher)

        engine.dispose()

        reload_engine = create_persistence_engine(database_url)
        reload_factory = create_session_factory(reload_engine)
        try:
            with reload_factory() as reload_session:
                reloaded_supplier = SqlAlchemySupplierRepository(reload_session).get(supplier_id)
                reloaded_relationship = SqlAlchemySupplierRelationshipRepository(
                    reload_session
                ).get(relationship_id)
                reloaded_onboarding = SqlAlchemySupplierOnboardingRepository(
                    reload_session
                ).find_for_relationship(relationship_id)
                reloaded_assessment = SqlAlchemySupplierAssessmentRepository(
                    reload_session
                ).get(assessment_id)
                reloaded_qualification = SqlAlchemySupplierQualificationRepository(
                    reload_session
                ).get(qualification_id)

                assert reloaded_relationship is not None
                assert reloaded_onboarding is not None
                assert reloaded_assessment is not None
                assert reloaded_assessment.score is not None
                assert reloaded_qualification is not None
                assert reloaded_qualification.decision is not None

                return PersistentQualificationOutcome(
                    supplier_exists=reloaded_supplier is not None,
                    relationship_exists=True,
                    relationship_stage=reloaded_relationship.stage,
                    onboarding_complete=reloaded_onboarding.is_complete,
                    assessment_complete=reloaded_assessment.is_complete,
                    assessment_score=reloaded_assessment.score.value,
                    qualification_scope=reloaded_qualification.scope,
                    qualification_status=reloaded_qualification.status,
                    qualification_decision=reloaded_qualification.decision,
                    observed_events=tuple(observed_events),
                )
        finally:
            reload_engine.dispose()
    finally:
        engine.dispose()


def main() -> None:
    """Run a disposable SQLite persistent qualification demonstration."""

    with TemporaryDirectory() as directory:
        database_path = Path(directory) / "pysrmkit-persistent-demo.db"
        outcome = run_persistent_qualification(f"sqlite:///{database_path}")

    for event_name in outcome.observed_events:
        print(f"[EVENT] {event_name}")
    print(f"[RESULT] Qualification status after reload: {outcome.qualification_status}")


if __name__ == "__main__":
    main()
