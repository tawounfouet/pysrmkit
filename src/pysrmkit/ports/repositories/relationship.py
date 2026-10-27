"""Repository contract for the SupplierRelationship Aggregate Root."""

from __future__ import annotations

from typing import Protocol

from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId


class SupplierRelationshipRepository(Protocol):
    """Persistence abstraction required by Supplier Relationship use cases."""

    def get(
        self,
        relationship_id: SupplierRelationshipId,
    ) -> SupplierRelationship | None: ...

    def save(self, relationship: SupplierRelationship) -> None: ...

    def find_for_supplier_and_organization(
        self,
        supplier_id: SupplierId,
        organization_id: InternalOrganizationId,
    ) -> SupplierRelationship | None: ...
