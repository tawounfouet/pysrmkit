"""SupplierOnboarding Domain ↔ SQLAlchemy mapper tests."""

from datetime import UTC, datetime

from pysrmkit.adapters.sqlalchemy.mappers.onboarding import (
    new_onboarding_record,
    onboarding_from_record,
)
from pysrmkit.domain.onboarding.entities import SupplierOnboarding
from pysrmkit.domain.onboarding.value_objects import (
    OnboardingId,
    OnboardingRequirement,
    OnboardingRequirementCode,
)
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId

STARTED = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
COMPLETED = datetime(2026, 10, 27, 13, 0, tzinfo=UTC)


def test_onboarding_mapper_preserves_requirements_order_and_completion() -> None:
    onboarding = SupplierOnboarding.reconstitute(
        onboarding_id=OnboardingId.new(),
        relationship_id=SupplierRelationshipId.new(),
        started_at=STARTED,
        requirements=(
            OnboardingRequirement(
                code=OnboardingRequirementCode("LEGAL"),
                mandatory=True,
                satisfied=True,
            ),
            OnboardingRequirement(
                code=OnboardingRequirementCode("BANK"),
                mandatory=False,
                satisfied=False,
            ),
        ),
        completed_at=COMPLETED,
    )

    record = new_onboarding_record(onboarding)
    restored = onboarding_from_record(record)

    assert restored == onboarding
    assert restored.relationship_id == onboarding.relationship_id
    assert restored.started_at == STARTED
    assert restored.completed_at == COMPLETED
    assert restored.requirements == onboarding.requirements
    assert restored.pull_events() == ()
