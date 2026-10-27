"""Application results for Supplier Relationship use cases."""

from dataclasses import dataclass

from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId


@dataclass(frozen=True, slots=True)
class CreateSupplierRelationshipResult:
    """Result returned after a SupplierRelationship is created successfully."""

    relationship_id: SupplierRelationshipId
