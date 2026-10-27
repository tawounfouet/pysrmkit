"""Shared behavioral contract for SupplierOnboardingRepository implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta

from pysrmkit.domain.onboarding.entities import SupplierOnboarding
from pysrmkit.domain.onboarding.value_objects import (
    OnboardingId,
    OnboardingRequirement,
    OnboardingRequirementCode,
)
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId
from pysrmkit.ports.repositories.onboarding import SupplierOnboardingRepository

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
LATER = NOW + timedelta(hours=1)


def make_onboarding(
    *,
    relationship_id: SupplierRelationshipId | None = None,
) -> SupplierOnboarding:
    return SupplierOnboarding.create(
        onboarding_id=OnboardingId.new(),
        relationship_id=relationship_id or SupplierRelationshipId.new(),
        started_at=NOW,
        requirements=(OnboardingRequirement(code=OnboardingRequirementCode("LEGAL_NAME")),),
    )


class SupplierOnboardingRepositoryContract(ABC):
    """Behavior every SupplierOnboardingRepository adapter must preserve."""

    @abstractmethod
    def make_repository(self) -> SupplierOnboardingRepository:
        raise NotImplementedError

    def test_save_then_get_returns_same_logical_onboarding(self) -> None:
        repository = self.make_repository()
        onboarding = make_onboarding()

        repository.save(onboarding)
        loaded = repository.get(onboarding.id)

        assert loaded is not None
        assert loaded == onboarding
        assert loaded.relationship_id == onboarding.relationship_id
        assert loaded.requirements == onboarding.requirements

    def test_unknown_id_returns_none(self) -> None:
        repository = self.make_repository()

        assert repository.get(OnboardingId.new()) is None

    def test_find_for_relationship_returns_onboarding(self) -> None:
        repository = self.make_repository()
        relationship_id = SupplierRelationshipId.new()
        onboarding = make_onboarding(relationship_id=relationship_id)
        repository.save(onboarding)

        loaded = repository.find_for_relationship(relationship_id)

        assert loaded is not None
        assert loaded.id == onboarding.id

    def test_unknown_relationship_returns_none(self) -> None:
        repository = self.make_repository()

        assert repository.find_for_relationship(SupplierRelationshipId.new()) is None

    def test_satisfied_requirements_survive_explicit_save_and_reload(self) -> None:
        repository = self.make_repository()
        onboarding = make_onboarding()
        repository.save(onboarding)

        loaded = repository.get(onboarding.id)
        assert loaded is not None
        loaded.satisfy_requirement(OnboardingRequirementCode("LEGAL_NAME"))
        repository.save(loaded)

        reloaded = repository.get(onboarding.id)
        assert reloaded is not None
        assert reloaded.progress.satisfied_requirements == 1
        assert reloaded.progress.ready_for_completion is True

    def test_completed_state_survives_explicit_save_and_reload(self) -> None:
        repository = self.make_repository()
        onboarding = make_onboarding()
        onboarding.satisfy_requirement(OnboardingRequirementCode("LEGAL_NAME"))
        onboarding.complete(occurred_at=LATER)
        onboarding.pull_events()
        repository.save(onboarding)

        reloaded = repository.get(onboarding.id)

        assert reloaded is not None
        assert reloaded.is_complete is True
        assert reloaded.completed_at == LATER
        assert reloaded.pull_events() == ()

    def test_unsaved_requirement_change_does_not_leak_into_repository_state(self) -> None:
        repository = self.make_repository()
        onboarding = make_onboarding()
        repository.save(onboarding)

        loaded = repository.get(onboarding.id)
        assert loaded is not None
        loaded.satisfy_requirement(OnboardingRequirementCode("LEGAL_NAME"))

        unchanged = repository.get(onboarding.id)
        assert unchanged is not None
        assert unchanged.progress.satisfied_requirements == 0

    def test_onboardings_for_different_relationships_remain_isolated(self) -> None:
        repository = self.make_repository()
        first = make_onboarding()
        second = make_onboarding()
        repository.save(first)
        repository.save(second)

        loaded_first = repository.find_for_relationship(first.relationship_id)
        loaded_second = repository.find_for_relationship(second.relationship_id)

        assert loaded_first is not None
        assert loaded_second is not None
        assert loaded_first.id == first.id
        assert loaded_second.id == second.id
        assert loaded_first.id != loaded_second.id
