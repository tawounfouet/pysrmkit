"""Repository contract for the SupplierOnboarding Aggregate Root."""

from __future__ import annotations

from typing import Protocol

from pysrmkit.domain.onboarding.entities import SupplierOnboarding
from pysrmkit.domain.onboarding.value_objects import OnboardingId
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


class SupplierOnboardingRepository(Protocol):
    """Persistence abstraction required by Supplier Onboarding use cases."""

    def get(self, onboarding_id: OnboardingId) -> SupplierOnboarding | None: ...

    def save(self, onboarding: SupplierOnboarding) -> None: ...

    def find_for_relationship(
        self,
        relationship_id: SupplierRelationshipId,
    ) -> SupplierOnboarding | None: ...
