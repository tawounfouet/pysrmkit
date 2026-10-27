"""In-memory implementation of SupplierRelationshipRepository."""

from __future__ import annotations

from dataclasses import dataclass

from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierLifecycleStage,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId


@dataclass(frozen=True, slots=True)
class _StoredRelationship:
    relationship_id: SupplierRelationshipId
    supplier_id: SupplierId
    organization_id: InternalOrganizationId
    stage: SupplierLifecycleStage


class InMemorySupplierRelationshipRepository:
    """Persistence-like in-memory repository for SupplierRelationship Aggregates."""

    def __init__(self) -> None:
        self._relationships: dict[SupplierRelationshipId, _StoredRelationship] = {}

    def get(
        self,
        relationship_id: SupplierRelationshipId,
    ) -> SupplierRelationship | None:
        stored = self._relationships.get(relationship_id)
        if stored is None:
            return None
        return self._restore(stored)

    def save(self, relationship: SupplierRelationship) -> None:
        self._relationships[relationship.id] = _StoredRelationship(
            relationship_id=relationship.id,
            supplier_id=relationship.supplier_id,
            organization_id=relationship.organization_id,
            stage=relationship.stage,
        )

    def _snapshot_state(self) -> dict[SupplierRelationshipId, _StoredRelationship]:
        """Return an adapter-internal snapshot for transactional rollback."""

        return dict(self._relationships)

    def _restore_state(
        self,
        snapshot: dict[SupplierRelationshipId, _StoredRelationship],
    ) -> None:
        """Restore a previously captured adapter-internal snapshot."""

        self._relationships = dict(snapshot)

    def find_for_supplier_and_organization(
        self,
        supplier_id: SupplierId,
        organization_id: InternalOrganizationId,
    ) -> SupplierRelationship | None:
        for stored in self._relationships.values():
            if stored.supplier_id == supplier_id and stored.organization_id == organization_id:
                return self._restore(stored)
        return None

    @staticmethod
    def _restore(stored: _StoredRelationship) -> SupplierRelationship:
        return SupplierRelationship.reconstitute(
            relationship_id=stored.relationship_id,
            supplier_id=stored.supplier_id,
            organization_id=stored.organization_id,
            stage=stored.stage,
        )
