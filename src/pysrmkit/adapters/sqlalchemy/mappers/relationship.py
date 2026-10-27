"""Explicit mapping between SupplierRelationship Domain state and persistence records."""

from pysrmkit.adapters.sqlalchemy.models.relationship import SupplierRelationshipRecord
from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierLifecycleStage,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId


def new_relationship_record(
    relationship: SupplierRelationship,
) -> SupplierRelationshipRecord:
    """Create a new persistence record from current Relationship state."""

    return SupplierRelationshipRecord(
        relationship_id=relationship.id.value,
        supplier_id=relationship.supplier_id.value,
        organization_id=relationship.organization_id.value,
        stage=relationship.stage.value,
    )


def apply_relationship_state(
    record: SupplierRelationshipRecord,
    relationship: SupplierRelationship,
) -> None:
    """Synchronize an existing persistence record from a Relationship Aggregate."""

    record.supplier_id = relationship.supplier_id.value
    record.organization_id = relationship.organization_id.value
    record.stage = relationship.stage.value


def relationship_from_record(record: SupplierRelationshipRecord) -> SupplierRelationship:
    """Reconstitute a persistence-ignorant SupplierRelationship Aggregate."""

    return SupplierRelationship.reconstitute(
        relationship_id=SupplierRelationshipId(record.relationship_id),
        supplier_id=SupplierId(record.supplier_id),
        organization_id=InternalOrganizationId(record.organization_id),
        stage=SupplierLifecycleStage(record.stage),
    )
