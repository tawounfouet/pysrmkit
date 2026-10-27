"""Shared behavioral contract for SupplierRelationshipRepository implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime

from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierLifecycleStage,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId
from pysrmkit.ports.repositories.relationship import SupplierRelationshipRepository

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


def make_relationship(
    *,
    supplier_id: SupplierId | None = None,
    organization_id: InternalOrganizationId | None = None,
) -> SupplierRelationship:
    return SupplierRelationship.create(
        relationship_id=SupplierRelationshipId.new(),
        supplier_id=supplier_id or SupplierId.new(),
        organization_id=organization_id or InternalOrganizationId("ORG-A"),
        occurred_at=NOW,
    )


class SupplierRelationshipRepositoryContract(ABC):
    """Behavior every SupplierRelationshipRepository adapter must preserve."""

    @abstractmethod
    def make_repository(self) -> SupplierRelationshipRepository:
        raise NotImplementedError

    def test_save_then_get_returns_same_logical_relationship(self) -> None:
        repository = self.make_repository()
        relationship = make_relationship()

        repository.save(relationship)
        loaded = repository.get(relationship.id)

        assert loaded is not None
        assert loaded == relationship
        assert loaded.supplier_id == relationship.supplier_id
        assert loaded.organization_id == relationship.organization_id

    def test_unknown_id_returns_none(self) -> None:
        repository = self.make_repository()

        assert repository.get(SupplierRelationshipId.new()) is None

    def test_find_for_supplier_and_organization_resolves_relationship(self) -> None:
        repository = self.make_repository()
        supplier_id = SupplierId.new()
        organization_id = InternalOrganizationId("ORG-A")
        relationship = make_relationship(
            supplier_id=supplier_id,
            organization_id=organization_id,
        )
        repository.save(relationship)

        loaded = repository.find_for_supplier_and_organization(supplier_id, organization_id)

        assert loaded is not None
        assert loaded.id == relationship.id

    def test_unrelated_organization_does_not_match(self) -> None:
        repository = self.make_repository()
        supplier_id = SupplierId.new()
        relationship = make_relationship(
            supplier_id=supplier_id,
            organization_id=InternalOrganizationId("ORG-A"),
        )
        repository.save(relationship)

        assert (
            repository.find_for_supplier_and_organization(
                supplier_id,
                InternalOrganizationId("ORG-B"),
            )
            is None
        )

    def test_multiple_suppliers_remain_isolated(self) -> None:
        repository = self.make_repository()
        organization_id = InternalOrganizationId("ORG-A")
        first_supplier = SupplierId.new()
        second_supplier = SupplierId.new()
        first = make_relationship(
            supplier_id=first_supplier,
            organization_id=organization_id,
        )
        second = make_relationship(
            supplier_id=second_supplier,
            organization_id=organization_id,
        )
        repository.save(first)
        repository.save(second)

        loaded_first = repository.find_for_supplier_and_organization(
            first_supplier,
            organization_id,
        )
        loaded_second = repository.find_for_supplier_and_organization(
            second_supplier,
            organization_id,
        )

        assert loaded_first is not None
        assert loaded_second is not None
        assert loaded_first.id == first.id
        assert loaded_second.id == second.id

    def test_same_supplier_can_have_independent_organization_relationships(self) -> None:
        repository = self.make_repository()
        supplier_id = SupplierId.new()
        first = make_relationship(
            supplier_id=supplier_id,
            organization_id=InternalOrganizationId("ORG-A"),
        )
        second = make_relationship(
            supplier_id=supplier_id,
            organization_id=InternalOrganizationId("ORG-B"),
        )
        repository.save(first)
        repository.save(second)

        loaded_first = repository.find_for_supplier_and_organization(
            supplier_id,
            InternalOrganizationId("ORG-A"),
        )
        loaded_second = repository.find_for_supplier_and_organization(
            supplier_id,
            InternalOrganizationId("ORG-B"),
        )

        assert loaded_first is not None
        assert loaded_second is not None
        assert loaded_first.id != loaded_second.id

    def test_updated_lifecycle_persists_after_save(self) -> None:
        repository = self.make_repository()
        relationship = make_relationship()
        relationship.pull_events()
        repository.save(relationship)

        loaded = repository.get(relationship.id)
        assert loaded is not None
        loaded.invite(occurred_at=NOW)
        loaded.pull_events()
        repository.save(loaded)

        invited = repository.get(relationship.id)
        assert invited is not None
        assert invited.stage is SupplierLifecycleStage.INVITED

        invited.start_onboarding(occurred_at=NOW)
        invited.pull_events()
        repository.save(invited)

        onboarding = repository.get(relationship.id)
        assert onboarding is not None
        assert onboarding.stage is SupplierLifecycleStage.ONBOARDING

    def test_unsaved_lifecycle_transition_does_not_leak_into_repository_state(self) -> None:
        repository = self.make_repository()
        relationship = make_relationship()
        relationship.pull_events()
        repository.save(relationship)

        loaded = repository.get(relationship.id)
        assert loaded is not None
        loaded.invite(occurred_at=NOW)

        unchanged = repository.get(relationship.id)
        assert unchanged is not None
        assert unchanged.stage is SupplierLifecycleStage.DISCOVERED
