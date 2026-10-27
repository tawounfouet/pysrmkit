"""SupplierRelationship lifecycle state-machine tests."""

from datetime import UTC, datetime, timedelta

import pytest

from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.errors import InvalidLifecycleTransition
from pysrmkit.domain.relationship.events import SupplierInvited, SupplierOnboardingStarted
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    LifecycleTransitionReason,
    SupplierLifecycleStage,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)
LATER = NOW + timedelta(hours=1)


def make_relationship(
    stage: SupplierLifecycleStage = SupplierLifecycleStage.DISCOVERED,
) -> SupplierRelationship:
    return SupplierRelationship.reconstitute(
        relationship_id=SupplierRelationshipId.new(),
        supplier_id=SupplierId.new(),
        organization_id=InternalOrganizationId("ORG-A"),
        stage=stage,
    )


def test_lifecycle_stage_exposes_reference_baseline() -> None:
    assert tuple(SupplierLifecycleStage) == (
        SupplierLifecycleStage.DISCOVERED,
        SupplierLifecycleStage.PROSPECTIVE,
        SupplierLifecycleStage.INVITED,
        SupplierLifecycleStage.ONBOARDING,
        SupplierLifecycleStage.UNDER_REVIEW,
        SupplierLifecycleStage.QUALIFIED,
        SupplierLifecycleStage.ACTIVE,
        SupplierLifecycleStage.SUSPENDED,
        SupplierLifecycleStage.BLOCKED,
        SupplierLifecycleStage.INACTIVE,
        SupplierLifecycleStage.OFFBOARDED,
    )


def test_lifecycle_transition_reason_is_a_non_blank_value_object() -> None:
    reason = LifecycleTransitionReason("  Compliance review  ")

    assert reason.value == "Compliance review"
    assert str(reason) == "Compliance review"
    assert reason == LifecycleTransitionReason("Compliance review")

    with pytest.raises(ValueError):
        LifecycleTransitionReason("   ")


def test_invite_moves_discovered_relationship_to_invited_and_records_event() -> None:
    relationship = make_relationship()

    relationship.invite(occurred_at=NOW)

    assert relationship.stage is SupplierLifecycleStage.INVITED
    events = relationship.pull_events()
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, SupplierInvited)
    assert event.relationship_id == relationship.id
    assert event.supplier_id == relationship.supplier_id
    assert event.occurred_at == NOW


def test_invite_is_also_allowed_from_prospective_reference_stage() -> None:
    relationship = make_relationship(SupplierLifecycleStage.PROSPECTIVE)

    relationship.invite(occurred_at=NOW)

    assert relationship.stage is SupplierLifecycleStage.INVITED
    assert isinstance(relationship.pull_events()[0], SupplierInvited)


@pytest.mark.parametrize(
    "source",
    [
        SupplierLifecycleStage.INVITED,
        SupplierLifecycleStage.ONBOARDING,
        SupplierLifecycleStage.UNDER_REVIEW,
        SupplierLifecycleStage.ACTIVE,
        SupplierLifecycleStage.OFFBOARDED,
    ],
)
def test_invite_rejects_forbidden_source_stages_without_mutation_or_event(
    source: SupplierLifecycleStage,
) -> None:
    relationship = make_relationship(source)

    with pytest.raises(InvalidLifecycleTransition) as captured:
        relationship.invite(occurred_at=NOW)

    assert captured.value.source is source
    assert captured.value.target is SupplierLifecycleStage.INVITED
    assert relationship.stage is source
    assert relationship.pull_events() == ()


def test_start_onboarding_moves_invited_relationship_and_records_event() -> None:
    relationship = make_relationship(SupplierLifecycleStage.INVITED)

    relationship.start_onboarding(occurred_at=NOW)

    assert relationship.stage is SupplierLifecycleStage.ONBOARDING
    events = relationship.pull_events()
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, SupplierOnboardingStarted)
    assert event.relationship_id == relationship.id
    assert event.occurred_at == NOW


@pytest.mark.parametrize(
    "source",
    [
        SupplierLifecycleStage.DISCOVERED,
        SupplierLifecycleStage.PROSPECTIVE,
        SupplierLifecycleStage.ONBOARDING,
        SupplierLifecycleStage.UNDER_REVIEW,
        SupplierLifecycleStage.ACTIVE,
        SupplierLifecycleStage.OFFBOARDED,
    ],
)
def test_start_onboarding_rejects_forbidden_source_stages_without_event(
    source: SupplierLifecycleStage,
) -> None:
    relationship = make_relationship(source)

    with pytest.raises(InvalidLifecycleTransition) as captured:
        relationship.start_onboarding(occurred_at=NOW)

    assert captured.value.source is source
    assert captured.value.target is SupplierLifecycleStage.ONBOARDING
    assert relationship.stage is source
    assert relationship.pull_events() == ()


def test_creation_to_onboarding_path_uses_explicit_domain_behaviors() -> None:
    relationship = make_relationship()

    relationship.invite(occurred_at=NOW)
    invited_events = relationship.pull_events()
    relationship.start_onboarding(occurred_at=LATER)
    onboarding_events = relationship.pull_events()

    assert relationship.stage is SupplierLifecycleStage.ONBOARDING
    assert isinstance(invited_events[0], SupplierInvited)
    assert isinstance(onboarding_events[0], SupplierOnboardingStarted)
