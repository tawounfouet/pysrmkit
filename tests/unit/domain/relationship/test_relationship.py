"""SupplierRelationship Aggregate tests."""

from datetime import UTC, datetime

from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.events import SupplierRelationshipCreated
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


def test_relationship_creation_references_supplier_and_organization() -> None:
    relationship_id = SupplierRelationshipId.new()
    supplier_id = SupplierId.new()
    organization_id = InternalOrganizationId("ORG-A")

    relationship = SupplierRelationship.create(
        relationship_id=relationship_id,
        supplier_id=supplier_id,
        organization_id=organization_id,
        occurred_at=NOW,
    )

    assert relationship.id == relationship_id
    assert relationship.supplier_id == supplier_id
    assert relationship.organization_id == organization_id
    assert relationship.stage == "DISCOVERED"


def test_relationship_creation_records_supplier_relationship_created() -> None:
    relationship_id = SupplierRelationshipId.new()
    supplier_id = SupplierId.new()
    organization_id = InternalOrganizationId("ORG-A")
    relationship = SupplierRelationship.create(
        relationship_id=relationship_id,
        supplier_id=supplier_id,
        organization_id=organization_id,
        occurred_at=NOW,
    )

    events = relationship.pull_events()

    assert len(events) == 1
    event = events[0]
    assert isinstance(event, SupplierRelationshipCreated)
    assert event.relationship_id == relationship_id
    assert event.supplier_id == supplier_id
    assert event.organization_id == organization_id
    assert event.occurred_at == NOW
    assert relationship.pull_events() == ()


def test_reconstituted_relationship_does_not_recreate_creation_event() -> None:
    relationship = SupplierRelationship.reconstitute(
        relationship_id=SupplierRelationshipId.new(),
        supplier_id=SupplierId.new(),
        organization_id=InternalOrganizationId("ORG-A"),
    )

    assert relationship.stage == "DISCOVERED"
    assert relationship.pull_events() == ()


def test_relationship_entity_equality_uses_relationship_id() -> None:
    relationship_id = SupplierRelationshipId.new()
    supplier_id = SupplierId.new()
    left = SupplierRelationship.reconstitute(
        relationship_id=relationship_id,
        supplier_id=supplier_id,
        organization_id=InternalOrganizationId("ORG-A"),
    )
    right = SupplierRelationship.reconstitute(
        relationship_id=relationship_id,
        supplier_id=supplier_id,
        organization_id=InternalOrganizationId("ORG-B"),
    )
    another = SupplierRelationship.reconstitute(
        relationship_id=SupplierRelationshipId.new(),
        supplier_id=supplier_id,
        organization_id=InternalOrganizationId("ORG-A"),
    )

    assert left == right
    assert left != another
    assert left != object()
