"""In-memory implementation of SupplierOnboardingRepository."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pysrmkit.domain.onboarding.entities import SupplierOnboarding
from pysrmkit.domain.onboarding.value_objects import (
    OnboardingId,
    OnboardingRequirement,
)
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


@dataclass(frozen=True, slots=True)
class _StoredOnboarding:
    onboarding_id: OnboardingId
    relationship_id: SupplierRelationshipId
    started_at: datetime
    requirements: tuple[OnboardingRequirement, ...]
    completed_at: datetime | None


class InMemorySupplierOnboardingRepository:
    """Persistence-like in-memory repository for SupplierOnboarding Aggregates."""

    def __init__(self) -> None:
        self._onboardings: dict[OnboardingId, _StoredOnboarding] = {}

    def get(self, onboarding_id: OnboardingId) -> SupplierOnboarding | None:
        stored = self._onboardings.get(onboarding_id)
        if stored is None:
            return None
        return self._restore(stored)

    def save(self, onboarding: SupplierOnboarding) -> None:
        self._onboardings[onboarding.id] = _StoredOnboarding(
            onboarding_id=onboarding.id,
            relationship_id=onboarding.relationship_id,
            started_at=onboarding.started_at,
            requirements=onboarding.requirements,
            completed_at=onboarding.completed_at,
        )

    def _snapshot_state(self) -> dict[OnboardingId, _StoredOnboarding]:
        """Return an adapter-internal snapshot for transactional rollback."""

        return dict(self._onboardings)

    def _restore_state(
        self,
        snapshot: dict[OnboardingId, _StoredOnboarding],
    ) -> None:
        """Restore a previously captured adapter-internal snapshot."""

        self._onboardings = dict(snapshot)

    def find_for_relationship(
        self,
        relationship_id: SupplierRelationshipId,
    ) -> SupplierOnboarding | None:
        for stored in self._onboardings.values():
            if stored.relationship_id == relationship_id:
                return self._restore(stored)
        return None

    @staticmethod
    def _restore(stored: _StoredOnboarding) -> SupplierOnboarding:
        return SupplierOnboarding.reconstitute(
            onboarding_id=stored.onboarding_id,
            relationship_id=stored.relationship_id,
            started_at=stored.started_at,
            requirements=stored.requirements,
            completed_at=stored.completed_at,
        )
