"""SupplierRelationship Domain ↔ SQLAlchemy mapper tests."""

from pysrmkit.adapters.sqlalchemy.mappers.relationship import (
    new_relationship_record,
    relationship_from_record,
)
from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierLifecycleStage,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId


def test_relationship_mapper_preserves_identity_context_and_stage() -> None:
    relationship = SupplierRelationship.reconstitute(
        relationship_id=SupplierRelationshipId.new(),
        supplier_id=SupplierId.new(),
        organization_id=InternalOrganizationId(" ORG-PARIS "),
        stage=SupplierLifecycleStage.ONBOARDING,
    )

    record = new_relationship_record(relationship)
    restored = relationship_from_record(record)

    assert restored == relationship
    assert restored.supplier_id == relationship.supplier_id
    assert restored.organization_id == relationship.organization_id
    assert restored.stage is SupplierLifecycleStage.ONBOARDING
    assert restored.pull_events() == ()
