"""SupplierRelationship lifecycle application-flow tests."""

from datetime import UTC, datetime, timedelta

import pytest

from pysrmkit.adapters.clock.fixed import FixedClock
from pysrmkit.adapters.memory.onboarding_repository import InMemorySupplierOnboardingRepository
from pysrmkit.adapters.memory.relationship_repository import (
    InMemorySupplierRelationshipRepository,
)
from pysrmkit.application.onboarding.commands import OnboardingRequirementInput
from pysrmkit.application.onboarding.errors import SupplierOnboardingAlreadyExists
from pysrmkit.application.relationship.commands import (
    InviteSupplierRelationship,
    StartSupplierOnboarding,
)
from pysrmkit.application.relationship.errors import SupplierRelationshipNotFound
from pysrmkit.application.relationship.handlers import (
    InviteSupplierRelationshipHandler,
    StartSupplierOnboardingHandler,
)
from pysrmkit.domain.common.events import DomainEvent
from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.errors import InvalidLifecycleTransition
from pysrmkit.domain.relationship.events import SupplierInvited, SupplierOnboardingStarted
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierLifecycleStage,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
LATER = NOW + timedelta(hours=1)


class RecordingEventDispatcher:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def dispatch(self, events: tuple[DomainEvent, ...]) -> None:
        self.events.extend(events)


def save_relationship(
    repository: InMemorySupplierRelationshipRepository,
    *,
    supplier_id: SupplierId | None = None,
    organization_id: InternalOrganizationId | None = None,
) -> SupplierRelationshipId:
    relationship = SupplierRelationship.create(
        relationship_id=SupplierRelationshipId.new(),
        supplier_id=supplier_id or SupplierId.new(),
        organization_id=organization_id or InternalOrganizationId("ORG-A"),
        occurred_at=NOW,
    )
    relationship.pull_events()
    repository.save(relationship)
    return relationship.id


def test_invite_handler_persists_transition_and_dispatches_event() -> None:
    repository = InMemorySupplierRelationshipRepository()
    dispatcher = RecordingEventDispatcher()
    relationship_id = save_relationship(repository)
    handler = InviteSupplierRelationshipHandler(
        relationship_repository=repository,
        clock=FixedClock(NOW),
        event_dispatcher=dispatcher,
    )

    handler.handle(InviteSupplierRelationship(relationship_id=relationship_id))

    loaded = repository.get(relationship_id)
    assert loaded is not None
    assert loaded.stage is SupplierLifecycleStage.INVITED
    assert len(dispatcher.events) == 1
    assert isinstance(dispatcher.events[0], SupplierInvited)


def test_invite_handler_raises_not_found_without_dispatch() -> None:
    repository = InMemorySupplierRelationshipRepository()
    dispatcher = RecordingEventDispatcher()
    handler = InviteSupplierRelationshipHandler(
        relationship_repository=repository,
        clock=FixedClock(NOW),
        event_dispatcher=dispatcher,
    )

    with pytest.raises(SupplierRelationshipNotFound):
        handler.handle(InviteSupplierRelationship(relationship_id=SupplierRelationshipId.new()))

    assert dispatcher.events == []


def test_start_onboarding_handler_persists_transition_and_creates_onboarding() -> None:
    repository = InMemorySupplierRelationshipRepository()
    onboardings = InMemorySupplierOnboardingRepository()
    dispatcher = RecordingEventDispatcher()
    relationship_id = save_relationship(repository)
    relationship = repository.get(relationship_id)
    assert relationship is not None
    relationship.invite(occurred_at=NOW)
    relationship.pull_events()
    repository.save(relationship)
    handler = StartSupplierOnboardingHandler(
        relationship_repository=repository,
        onboarding_repository=onboardings,
        clock=FixedClock(LATER),
        event_dispatcher=dispatcher,
    )

    handler.handle(
        StartSupplierOnboarding(
            relationship_id=relationship_id,
            requirements=(
                OnboardingRequirementInput(code="LEGAL_NAME"),
                OnboardingRequirementInput(code="BANK_REFERENCE", mandatory=False),
            ),
        )
    )

    loaded = repository.get(relationship_id)
    assert loaded is not None
    assert loaded.stage is SupplierLifecycleStage.ONBOARDING
    onboarding = onboardings.find_for_relationship(relationship_id)
    assert onboarding is not None
    assert tuple(item.code.value for item in onboarding.requirements) == (
        "LEGAL_NAME",
        "BANK_REFERENCE",
    )
    assert len(dispatcher.events) == 1
    event = dispatcher.events[0]
    assert isinstance(event, SupplierOnboardingStarted)
    assert event.occurred_at == LATER


def test_start_onboarding_handler_raises_not_found_without_dispatch() -> None:
    repository = InMemorySupplierRelationshipRepository()
    onboardings = InMemorySupplierOnboardingRepository()
    dispatcher = RecordingEventDispatcher()
    handler = StartSupplierOnboardingHandler(
        relationship_repository=repository,
        onboarding_repository=onboardings,
        clock=FixedClock(NOW),
        event_dispatcher=dispatcher,
    )

    with pytest.raises(SupplierRelationshipNotFound):
        handler.handle(StartSupplierOnboarding(relationship_id=SupplierRelationshipId.new()))

    assert dispatcher.events == []


def test_failed_handler_transition_does_not_persist_or_dispatch() -> None:
    repository = InMemorySupplierRelationshipRepository()
    onboardings = InMemorySupplierOnboardingRepository()
    dispatcher = RecordingEventDispatcher()
    relationship_id = save_relationship(repository)
    handler = StartSupplierOnboardingHandler(
        relationship_repository=repository,
        onboarding_repository=onboardings,
        clock=FixedClock(NOW),
        event_dispatcher=dispatcher,
    )

    with pytest.raises(InvalidLifecycleTransition):
        handler.handle(StartSupplierOnboarding(relationship_id=relationship_id))

    loaded = repository.get(relationship_id)
    assert loaded is not None
    assert loaded.stage is SupplierLifecycleStage.DISCOVERED
    assert dispatcher.events == []


def test_lifecycle_transition_is_scoped_to_one_relationship() -> None:
    repository = InMemorySupplierRelationshipRepository()
    dispatcher = RecordingEventDispatcher()
    supplier_id = SupplierId.new()
    first_id = save_relationship(
        repository,
        supplier_id=supplier_id,
        organization_id=InternalOrganizationId("ORG-A"),
    )
    second_id = save_relationship(
        repository,
        supplier_id=supplier_id,
        organization_id=InternalOrganizationId("ORG-B"),
    )
    invite = InviteSupplierRelationshipHandler(
        relationship_repository=repository,
        clock=FixedClock(NOW),
        event_dispatcher=dispatcher,
    )
    onboardings = InMemorySupplierOnboardingRepository()
    onboarding = StartSupplierOnboardingHandler(
        relationship_repository=repository,
        onboarding_repository=onboardings,
        clock=FixedClock(LATER),
        event_dispatcher=dispatcher,
    )

    invite.handle(InviteSupplierRelationship(relationship_id=first_id))
    onboarding.handle(StartSupplierOnboarding(relationship_id=first_id))

    first = repository.get(first_id)
    second = repository.get(second_id)
    assert first is not None
    assert second is not None
    assert first.stage is SupplierLifecycleStage.ONBOARDING
    assert second.stage is SupplierLifecycleStage.DISCOVERED

def test_start_onboarding_rejects_second_onboarding_for_same_relationship() -> None:
    repository = InMemorySupplierRelationshipRepository()
    onboardings = InMemorySupplierOnboardingRepository()
    dispatcher = RecordingEventDispatcher()
    relationship_id = save_relationship(repository)
    relationship = repository.get(relationship_id)
    assert relationship is not None
    relationship.invite(occurred_at=NOW)
    relationship.pull_events()
    repository.save(relationship)
    handler = StartSupplierOnboardingHandler(
        relationship_repository=repository,
        onboarding_repository=onboardings,
        clock=FixedClock(LATER),
        event_dispatcher=dispatcher,
    )
    command = StartSupplierOnboarding(relationship_id=relationship_id)

    handler.handle(command)

    reloaded = repository.get(relationship_id)
    assert reloaded is not None
    assert reloaded.stage is SupplierLifecycleStage.ONBOARDING
    dispatcher.events.clear()

    with pytest.raises(SupplierOnboardingAlreadyExists):
        handler.handle(command)

    assert dispatcher.events == []
