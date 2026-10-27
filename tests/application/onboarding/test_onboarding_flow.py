"""Supplier Onboarding application-flow tests."""

from datetime import UTC, datetime, timedelta

import pytest

from pysrmkit.adapters.clock.fixed import FixedClock
from pysrmkit.adapters.memory.onboarding_repository import InMemorySupplierOnboardingRepository
from pysrmkit.application.onboarding.commands import (
    CompleteSupplierOnboarding,
    SatisfyOnboardingRequirement,
)
from pysrmkit.application.onboarding.errors import SupplierOnboardingNotFound
from pysrmkit.application.onboarding.handlers import (
    CompleteSupplierOnboardingHandler,
    GetOnboardingProgressHandler,
    SatisfyOnboardingRequirementHandler,
)
from pysrmkit.application.onboarding.queries import GetOnboardingProgress
from pysrmkit.domain.common.events import DomainEvent
from pysrmkit.domain.onboarding.entities import SupplierOnboarding
from pysrmkit.domain.onboarding.errors import MandatoryOnboardingRequirementsNotSatisfied
from pysrmkit.domain.onboarding.events import SupplierOnboardingCompleted
from pysrmkit.domain.onboarding.value_objects import (
    OnboardingId,
    OnboardingRequirement,
    OnboardingRequirementCode,
)
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
LATER = NOW + timedelta(hours=1)


class RecordingEventDispatcher:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def dispatch(self, events: tuple[DomainEvent, ...]) -> None:
        self.events.extend(events)


def save_onboarding(repository: InMemorySupplierOnboardingRepository) -> OnboardingId:
    onboarding = SupplierOnboarding.create(
        onboarding_id=OnboardingId.new(),
        relationship_id=SupplierRelationshipId.new(),
        started_at=NOW,
        requirements=(
            OnboardingRequirement(code=OnboardingRequirementCode("LEGAL_NAME")),
            OnboardingRequirement(code=OnboardingRequirementCode("TAX_ID")),
            OnboardingRequirement(
                code=OnboardingRequirementCode("BANK_REFERENCE"),
                mandatory=False,
            ),
        ),
    )
    repository.save(onboarding)
    return onboarding.id


def test_satisfy_requirement_handler_persists_requirement_state() -> None:
    repository = InMemorySupplierOnboardingRepository()
    onboarding_id = save_onboarding(repository)
    handler = SatisfyOnboardingRequirementHandler(repository=repository)

    handler.handle(
        SatisfyOnboardingRequirement(
            onboarding_id=onboarding_id,
            requirement_code=OnboardingRequirementCode("LEGAL_NAME"),
        )
    )

    loaded = repository.get(onboarding_id)
    assert loaded is not None
    assert loaded.progress.satisfied_requirements == 1


def test_progress_query_returns_computed_readiness() -> None:
    repository = InMemorySupplierOnboardingRepository()
    onboarding_id = save_onboarding(repository)
    SatisfyOnboardingRequirementHandler(repository=repository).handle(
        SatisfyOnboardingRequirement(
            onboarding_id=onboarding_id,
            requirement_code=OnboardingRequirementCode("LEGAL_NAME"),
        )
    )
    query_handler = GetOnboardingProgressHandler(repository=repository)

    progress = query_handler.handle(GetOnboardingProgress(onboarding_id=onboarding_id))

    assert progress.total_requirements == 3
    assert progress.satisfied_requirements == 1
    assert progress.ready_for_completion is False
    assert progress.completed is False


def test_complete_handler_rejects_missing_mandatory_requirement_without_event() -> None:
    repository = InMemorySupplierOnboardingRepository()
    onboarding_id = save_onboarding(repository)
    dispatcher = RecordingEventDispatcher()
    handler = CompleteSupplierOnboardingHandler(
        repository=repository,
        clock=FixedClock(LATER),
        event_dispatcher=dispatcher,
    )

    with pytest.raises(MandatoryOnboardingRequirementsNotSatisfied):
        handler.handle(CompleteSupplierOnboarding(onboarding_id=onboarding_id))

    loaded = repository.get(onboarding_id)
    assert loaded is not None
    assert loaded.is_complete is False
    assert dispatcher.events == []


def test_complete_handler_persists_completion_and_dispatches_event() -> None:
    repository = InMemorySupplierOnboardingRepository()
    onboarding_id = save_onboarding(repository)
    satisfy = SatisfyOnboardingRequirementHandler(repository=repository)
    for code in ("LEGAL_NAME", "TAX_ID"):
        satisfy.handle(
            SatisfyOnboardingRequirement(
                onboarding_id=onboarding_id,
                requirement_code=OnboardingRequirementCode(code),
            )
        )
    dispatcher = RecordingEventDispatcher()
    handler = CompleteSupplierOnboardingHandler(
        repository=repository,
        clock=FixedClock(LATER),
        event_dispatcher=dispatcher,
    )

    handler.handle(CompleteSupplierOnboarding(onboarding_id=onboarding_id))

    loaded = repository.get(onboarding_id)
    assert loaded is not None
    assert loaded.is_complete is True
    assert loaded.completed_at == LATER
    assert len(dispatcher.events) == 1
    assert isinstance(dispatcher.events[0], SupplierOnboardingCompleted)


def test_onboarding_handlers_raise_not_found_for_missing_onboarding() -> None:
    repository = InMemorySupplierOnboardingRepository()
    missing = OnboardingId.new()

    with pytest.raises(SupplierOnboardingNotFound):
        SatisfyOnboardingRequirementHandler(repository=repository).handle(
            SatisfyOnboardingRequirement(
                onboarding_id=missing,
                requirement_code=OnboardingRequirementCode("LEGAL_NAME"),
            )
        )

    with pytest.raises(SupplierOnboardingNotFound):
        GetOnboardingProgressHandler(repository=repository).handle(
            GetOnboardingProgress(onboarding_id=missing)
        )
