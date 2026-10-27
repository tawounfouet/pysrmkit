"""SupplierOnboarding Aggregate tests."""

from datetime import UTC, datetime, timedelta

import pytest

from pysrmkit.domain.onboarding.entities import SupplierOnboarding
from pysrmkit.domain.onboarding.errors import (
    DuplicateOnboardingRequirement,
    MandatoryOnboardingRequirementsNotSatisfied,
    OnboardingAlreadyCompleted,
    UnknownOnboardingRequirement,
)
from pysrmkit.domain.onboarding.events import SupplierOnboardingCompleted
from pysrmkit.domain.onboarding.value_objects import (
    OnboardingId,
    OnboardingRequirement,
    OnboardingRequirementCode,
)
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
LATER = NOW + timedelta(hours=1)


def requirement(code: str, *, mandatory: bool = True) -> OnboardingRequirement:
    return OnboardingRequirement(
        code=OnboardingRequirementCode(code),
        mandatory=mandatory,
    )


def make_onboarding() -> SupplierOnboarding:
    return SupplierOnboarding.create(
        onboarding_id=OnboardingId.new(),
        relationship_id=SupplierRelationshipId.new(),
        started_at=NOW,
        requirements=(
            requirement("LEGAL_NAME"),
            requirement("TAX_ID"),
            requirement("BANK_REFERENCE", mandatory=False),
        ),
    )


def test_onboarding_is_relationship_scoped_and_starts_incomplete() -> None:
    relationship_id = SupplierRelationshipId.new()
    onboarding = SupplierOnboarding.create(
        onboarding_id=OnboardingId.new(),
        relationship_id=relationship_id,
        started_at=NOW,
        requirements=(requirement("LEGAL_NAME"),),
    )

    assert onboarding.relationship_id == relationship_id
    assert onboarding.started_at == NOW
    assert onboarding.is_complete is False
    assert onboarding.completed_at is None
    assert onboarding.pull_events() == ()


def test_duplicate_requirement_codes_are_rejected() -> None:
    duplicate = requirement("LEGAL_NAME")

    with pytest.raises(DuplicateOnboardingRequirement):
        SupplierOnboarding.create(
            onboarding_id=OnboardingId.new(),
            relationship_id=SupplierRelationshipId.new(),
            started_at=NOW,
            requirements=(duplicate, duplicate),
        )


def test_satisfying_requirement_updates_progress_without_mutating_other_requirements() -> None:
    onboarding = make_onboarding()

    onboarding.satisfy_requirement(OnboardingRequirementCode("LEGAL_NAME"))

    progress = onboarding.progress
    assert progress.total_requirements == 3
    assert progress.satisfied_requirements == 1
    assert progress.mandatory_requirements == 2
    assert progress.satisfied_mandatory_requirements == 1
    assert progress.missing_mandatory_requirements == (OnboardingRequirementCode("TAX_ID"),)
    assert progress.ready_for_completion is False
    assert progress.completed is False


def test_unknown_requirement_cannot_be_satisfied() -> None:
    onboarding = make_onboarding()

    with pytest.raises(UnknownOnboardingRequirement):
        onboarding.satisfy_requirement(OnboardingRequirementCode("UNKNOWN"))


def test_incomplete_onboarding_cannot_be_completed_and_records_no_event() -> None:
    onboarding = make_onboarding()
    onboarding.satisfy_requirement(OnboardingRequirementCode("LEGAL_NAME"))

    with pytest.raises(MandatoryOnboardingRequirementsNotSatisfied) as captured:
        onboarding.complete(occurred_at=LATER)

    assert captured.value.missing == (OnboardingRequirementCode("TAX_ID"),)
    assert onboarding.is_complete is False
    assert onboarding.completed_at is None
    assert onboarding.pull_events() == ()


def test_optional_requirement_does_not_block_completion() -> None:
    onboarding = make_onboarding()
    onboarding.satisfy_requirement(OnboardingRequirementCode("LEGAL_NAME"))
    onboarding.satisfy_requirement(OnboardingRequirementCode("TAX_ID"))

    onboarding.complete(occurred_at=LATER)

    assert onboarding.is_complete is True
    assert onboarding.completed_at == LATER
    progress = onboarding.progress
    assert progress.ready_for_completion is True
    assert progress.completed is True
    assert progress.satisfied_requirements == 2

    events = onboarding.pull_events()
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, SupplierOnboardingCompleted)
    assert event.onboarding_id == onboarding.id
    assert event.relationship_id == onboarding.relationship_id
    assert event.occurred_at == LATER


def test_completed_onboarding_cannot_be_mutated_or_completed_again() -> None:
    onboarding = SupplierOnboarding.create(
        onboarding_id=OnboardingId.new(),
        relationship_id=SupplierRelationshipId.new(),
        started_at=NOW,
    )
    onboarding.complete(occurred_at=LATER)
    onboarding.pull_events()

    with pytest.raises(OnboardingAlreadyCompleted):
        onboarding.satisfy_requirement(OnboardingRequirementCode("ANY"))

    with pytest.raises(OnboardingAlreadyCompleted):
        onboarding.complete(occurred_at=LATER)

    assert onboarding.pull_events() == ()


def test_reconstituted_onboarding_preserves_state_without_recreating_events() -> None:
    onboarding_id = OnboardingId.new()
    relationship_id = SupplierRelationshipId.new()
    onboarding = SupplierOnboarding.reconstitute(
        onboarding_id=onboarding_id,
        relationship_id=relationship_id,
        started_at=NOW,
        requirements=(
            OnboardingRequirement(
                code=OnboardingRequirementCode("LEGAL_NAME"),
                satisfied=True,
            ),
        ),
        completed_at=LATER,
    )

    assert onboarding.id == onboarding_id
    assert onboarding.relationship_id == relationship_id
    assert onboarding.is_complete is True
    assert onboarding.progress.completed is True
    assert onboarding.pull_events() == ()


def test_onboarding_entity_equality_uses_onboarding_id() -> None:
    onboarding_id = OnboardingId.new()
    relationship_id = SupplierRelationshipId.new()
    left = SupplierOnboarding.reconstitute(
        onboarding_id=onboarding_id,
        relationship_id=relationship_id,
        started_at=NOW,
    )
    right = SupplierOnboarding.reconstitute(
        onboarding_id=onboarding_id,
        relationship_id=SupplierRelationshipId.new(),
        started_at=LATER,
    )
    another = SupplierOnboarding.reconstitute(
        onboarding_id=OnboardingId.new(),
        relationship_id=relationship_id,
        started_at=NOW,
    )

    assert left == right
    assert left != another
    assert left != object()
