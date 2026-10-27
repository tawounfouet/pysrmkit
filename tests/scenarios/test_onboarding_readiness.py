"""Local onboarding-readiness vertical scenario."""

from datetime import UTC, datetime, timedelta

from pysrmkit.adapters.clock.fixed import FixedClock
from pysrmkit.adapters.memory.onboarding_repository import InMemorySupplierOnboardingRepository
from pysrmkit.adapters.memory.relationship_repository import (
    InMemorySupplierRelationshipRepository,
)
from pysrmkit.application.onboarding.commands import (
    CompleteSupplierOnboarding,
    OnboardingRequirementInput,
    SatisfyOnboardingRequirement,
)
from pysrmkit.application.onboarding.handlers import (
    CompleteSupplierOnboardingHandler,
    GetOnboardingProgressHandler,
    SatisfyOnboardingRequirementHandler,
)
from pysrmkit.application.onboarding.queries import GetOnboardingProgress
from pysrmkit.application.relationship.commands import (
    InviteSupplierRelationship,
    StartSupplierOnboarding,
)
from pysrmkit.application.relationship.handlers import (
    InviteSupplierRelationshipHandler,
    StartSupplierOnboardingHandler,
)
from pysrmkit.domain.common.events import DomainEvent
from pysrmkit.domain.onboarding.events import SupplierOnboardingCompleted
from pysrmkit.domain.onboarding.value_objects import OnboardingRequirementCode
from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.events import SupplierInvited, SupplierOnboardingStarted
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierLifecycleStage,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId

STARTED = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
ONBOARDING_AT = STARTED + timedelta(hours=1)
COMPLETED_AT = STARTED + timedelta(hours=2)


class RecordingEventDispatcher:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def dispatch(self, events: tuple[DomainEvent, ...]) -> None:
        self.events.extend(events)


def test_relationship_reaches_domain_valid_onboarding_readiness() -> None:
    relationships = InMemorySupplierRelationshipRepository()
    onboardings = InMemorySupplierOnboardingRepository()
    dispatcher = RecordingEventDispatcher()
    relationship = SupplierRelationship.create(
        relationship_id=SupplierRelationshipId.new(),
        supplier_id=SupplierId.new(),
        organization_id=InternalOrganizationId("ORG-A"),
        occurred_at=STARTED,
    )
    relationship.pull_events()
    relationships.save(relationship)

    InviteSupplierRelationshipHandler(
        relationship_repository=relationships,
        clock=FixedClock(STARTED),
        event_dispatcher=dispatcher,
    ).handle(InviteSupplierRelationship(relationship_id=relationship.id))

    StartSupplierOnboardingHandler(
        relationship_repository=relationships,
        onboarding_repository=onboardings,
        clock=FixedClock(ONBOARDING_AT),
        event_dispatcher=dispatcher,
    ).handle(
        StartSupplierOnboarding(
            relationship_id=relationship.id,
            requirements=(
                OnboardingRequirementInput(code="LEGAL_NAME"),
                OnboardingRequirementInput(code="TAX_ID"),
                OnboardingRequirementInput(code="BANK_REFERENCE", mandatory=False),
            ),
        )
    )

    onboarding = onboardings.find_for_relationship(relationship.id)
    assert onboarding is not None
    satisfy = SatisfyOnboardingRequirementHandler(repository=onboardings)
    for code in ("LEGAL_NAME", "TAX_ID"):
        satisfy.handle(
            SatisfyOnboardingRequirement(
                onboarding_id=onboarding.id,
                requirement_code=OnboardingRequirementCode(code),
            )
        )

    progress_before_completion = GetOnboardingProgressHandler(repository=onboardings).handle(
        GetOnboardingProgress(onboarding_id=onboarding.id)
    )
    assert progress_before_completion.ready_for_completion is True
    assert progress_before_completion.completed is False

    CompleteSupplierOnboardingHandler(
        repository=onboardings,
        clock=FixedClock(COMPLETED_AT),
        event_dispatcher=dispatcher,
    ).handle(CompleteSupplierOnboarding(onboarding_id=onboarding.id))

    persisted_relationship = relationships.get(relationship.id)
    completed = onboardings.get(onboarding.id)
    assert persisted_relationship is not None
    assert completed is not None
    assert persisted_relationship.stage is SupplierLifecycleStage.ONBOARDING
    assert completed.is_complete is True
    assert completed.progress.ready_for_completion is True
    assert completed.progress.completed is True
    assert [type(event) for event in dispatcher.events] == [
        SupplierInvited,
        SupplierOnboardingStarted,
        SupplierOnboardingCompleted,
    ]
