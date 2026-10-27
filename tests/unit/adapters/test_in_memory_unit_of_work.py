"""InMemory SupplierOnboarding UnitOfWork tests."""

from datetime import UTC, datetime

import pytest

from pysrmkit.adapters.memory.onboarding_repository import InMemorySupplierOnboardingRepository
from pysrmkit.adapters.memory.relationship_repository import (
    InMemorySupplierRelationshipRepository,
)
from pysrmkit.adapters.memory.unit_of_work import InMemorySupplierOnboardingUnitOfWork
from pysrmkit.domain.onboarding.entities import SupplierOnboarding
from pysrmkit.domain.onboarding.value_objects import OnboardingId
from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierLifecycleStage,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


def _invited_relationship() -> SupplierRelationship:
    relationship = SupplierRelationship.reconstitute(
        relationship_id=SupplierRelationshipId.new(),
        supplier_id=SupplierId.new(),
        organization_id=InternalOrganizationId("ORG-A"),
        stage=SupplierLifecycleStage.INVITED,
    )
    return relationship


def test_commit_keeps_both_in_memory_repository_changes() -> None:
    relationships = InMemorySupplierRelationshipRepository()
    onboardings = InMemorySupplierOnboardingRepository()
    relationship = _invited_relationship()
    relationships.save(relationship)
    unit_of_work = InMemorySupplierOnboardingUnitOfWork(
        relationship_repository=relationships,
        onboarding_repository=onboardings,
    )

    with unit_of_work as transaction:
        loaded = transaction.relationship_repository.get(relationship.id)
        assert loaded is not None
        loaded.start_onboarding(occurred_at=NOW)
        loaded.pull_events()
        transaction.relationship_repository.save(loaded)
        transaction.onboarding_repository.save(
            SupplierOnboarding.create(
                onboarding_id=OnboardingId.new(),
                relationship_id=loaded.id,
                started_at=NOW,
            )
        )
        transaction.commit()

    persisted = relationships.get(relationship.id)
    onboarding = onboardings.find_for_relationship(relationship.id)
    assert persisted is not None
    assert persisted.stage is SupplierLifecycleStage.ONBOARDING
    assert onboarding is not None


def test_exception_rolls_back_both_in_memory_repository_changes() -> None:
    relationships = InMemorySupplierRelationshipRepository()
    onboardings = InMemorySupplierOnboardingRepository()
    relationship = _invited_relationship()
    relationships.save(relationship)
    unit_of_work = InMemorySupplierOnboardingUnitOfWork(
        relationship_repository=relationships,
        onboarding_repository=onboardings,
    )

    with pytest.raises(RuntimeError, match="forced failure"):
        with unit_of_work as transaction:
            loaded = transaction.relationship_repository.get(relationship.id)
            assert loaded is not None
            loaded.start_onboarding(occurred_at=NOW)
            loaded.pull_events()
            transaction.relationship_repository.save(loaded)
            transaction.onboarding_repository.save(
                SupplierOnboarding.create(
                    onboarding_id=OnboardingId.new(),
                    relationship_id=loaded.id,
                    started_at=NOW,
                )
            )
            raise RuntimeError("forced failure")

    persisted = relationships.get(relationship.id)
    assert persisted is not None
    assert persisted.stage is SupplierLifecycleStage.INVITED
    assert onboardings.find_for_relationship(relationship.id) is None
