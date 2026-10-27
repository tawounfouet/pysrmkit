"""Domain Events emitted by SupplierOnboarding."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pysrmkit.domain.onboarding.value_objects import OnboardingId
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


@dataclass(frozen=True, slots=True)
class SupplierOnboardingCompleted:
    """Fact emitted after all mandatory onboarding requirements are satisfied."""

    event_id: UUID
    onboarding_id: OnboardingId
    relationship_id: SupplierRelationshipId
    occurred_at: datetime
