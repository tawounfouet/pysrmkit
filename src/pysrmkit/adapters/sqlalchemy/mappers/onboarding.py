"""Explicit mapping between SupplierOnboarding Domain state and persistence records."""

from pysrmkit.adapters.sqlalchemy.models.onboarding import (
    OnboardingRequirementRecord,
    SupplierOnboardingRecord,
)
from pysrmkit.domain.onboarding.entities import SupplierOnboarding
from pysrmkit.domain.onboarding.value_objects import (
    OnboardingId,
    OnboardingRequirement,
    OnboardingRequirementCode,
)
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


def _requirement_records(
    onboarding: SupplierOnboarding,
) -> list[OnboardingRequirementRecord]:
    return [
        OnboardingRequirementRecord(
            position=position,
            code=requirement.code.value,
            mandatory=requirement.mandatory,
            satisfied=requirement.satisfied,
        )
        for position, requirement in enumerate(onboarding.requirements)
    ]


def new_onboarding_record(onboarding: SupplierOnboarding) -> SupplierOnboardingRecord:
    """Create a new persistence record from current Onboarding state."""

    return SupplierOnboardingRecord(
        onboarding_id=onboarding.id.value,
        relationship_id=onboarding.relationship_id.value,
        started_at=onboarding.started_at,
        completed_at=onboarding.completed_at,
        requirements=_requirement_records(onboarding),
    )


def apply_onboarding_state(
    record: SupplierOnboardingRecord,
    onboarding: SupplierOnboarding,
) -> None:
    """Synchronize an existing persistence record from an Onboarding Aggregate."""

    record.relationship_id = onboarding.relationship_id.value
    record.started_at = onboarding.started_at
    record.completed_at = onboarding.completed_at
    record.requirements = _requirement_records(onboarding)


def onboarding_from_record(record: SupplierOnboardingRecord) -> SupplierOnboarding:
    """Reconstitute a persistence-ignorant SupplierOnboarding Aggregate."""

    return SupplierOnboarding.reconstitute(
        onboarding_id=OnboardingId(record.onboarding_id),
        relationship_id=SupplierRelationshipId(record.relationship_id),
        started_at=record.started_at,
        requirements=tuple(
            OnboardingRequirement(
                code=OnboardingRequirementCode(item.code),
                mandatory=item.mandatory,
                satisfied=item.satisfied,
            )
            for item in record.requirements
        ),
        completed_at=record.completed_at,
    )
