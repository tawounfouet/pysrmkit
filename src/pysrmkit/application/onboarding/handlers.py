"""Handlers orchestrating Supplier Onboarding use cases."""

from __future__ import annotations

from pysrmkit.application.onboarding.commands import (
    CompleteSupplierOnboarding,
    SatisfyOnboardingRequirement,
)
from pysrmkit.application.onboarding.errors import SupplierOnboardingNotFound
from pysrmkit.application.onboarding.queries import GetOnboardingProgress
from pysrmkit.domain.onboarding.entities import SupplierOnboarding
from pysrmkit.domain.onboarding.value_objects import OnboardingId, OnboardingProgress
from pysrmkit.ports.clock import Clock
from pysrmkit.ports.events import DomainEventDispatcher
from pysrmkit.ports.repositories.onboarding import SupplierOnboardingRepository


class _OnboardingLoader:
    def __init__(self, repository: SupplierOnboardingRepository) -> None:
        self._repository = repository

    def load(self, onboarding_id: OnboardingId) -> SupplierOnboarding:
        onboarding = self._repository.get(onboarding_id)
        if onboarding is None:
            raise SupplierOnboardingNotFound(f"SupplierOnboarding {onboarding_id} does not exist")
        return onboarding


class SatisfyOnboardingRequirementHandler:
    """Marks one requirement as satisfied and persists the onboarding."""

    def __init__(self, *, repository: SupplierOnboardingRepository) -> None:
        self._repository = repository
        self._loader = _OnboardingLoader(repository)

    def handle(self, command: SatisfyOnboardingRequirement) -> None:
        onboarding = self._loader.load(command.onboarding_id)
        onboarding.satisfy_requirement(command.requirement_code)
        self._repository.save(onboarding)


class CompleteSupplierOnboardingHandler:
    """Completes onboarding only when mandatory requirements are satisfied."""

    def __init__(
        self,
        *,
        repository: SupplierOnboardingRepository,
        clock: Clock,
        event_dispatcher: DomainEventDispatcher,
    ) -> None:
        self._repository = repository
        self._clock = clock
        self._event_dispatcher = event_dispatcher
        self._loader = _OnboardingLoader(repository)

    def handle(self, command: CompleteSupplierOnboarding) -> None:
        onboarding = self._loader.load(command.onboarding_id)
        onboarding.complete(occurred_at=self._clock.now())
        self._repository.save(onboarding)
        self._event_dispatcher.dispatch(onboarding.pull_events())


class GetOnboardingProgressHandler:
    """Returns computed readiness without introducing a mutable progress Entity."""

    def __init__(self, *, repository: SupplierOnboardingRepository) -> None:
        self._loader = _OnboardingLoader(repository)

    def handle(self, query: GetOnboardingProgress) -> OnboardingProgress:
        onboarding = self._loader.load(query.onboarding_id)
        return onboarding.progress
