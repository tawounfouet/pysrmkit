"""CreateSupplierRelationship application-flow tests."""

from datetime import UTC, datetime

import pytest

from pysrmkit.adapters.clock.fixed import FixedClock
from pysrmkit.adapters.memory.relationship_repository import (
    InMemorySupplierRelationshipRepository,
)
from pysrmkit.adapters.memory.supplier_repository import InMemorySupplierRepository
from pysrmkit.application.relationship.commands import CreateSupplierRelationship
from pysrmkit.application.relationship.errors import RelationshipAlreadyExists, SupplierNotFound
from pysrmkit.application.relationship.handlers import CreateSupplierRelationshipHandler
from pysrmkit.domain.common.events import DomainEvent
from pysrmkit.domain.relationship.events import SupplierRelationshipCreated
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierLifecycleStage,
)
from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import SupplierId, SupplierIdentity

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


class RecordingEventDispatcher:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def dispatch(self, events: tuple[DomainEvent, ...]) -> None:
        self.events.extend(events)


def save_supplier(repository: InMemorySupplierRepository) -> SupplierId:
    supplier = Supplier.create(
        supplier_id=SupplierId.new(),
        identity=SupplierIdentity(legal_name="ACME"),
        occurred_at=NOW,
    )
    repository.save(supplier)
    return supplier.id


def make_handler(
    supplier_repository: InMemorySupplierRepository,
    relationship_repository: InMemorySupplierRelationshipRepository,
    dispatcher: RecordingEventDispatcher,
) -> CreateSupplierRelationshipHandler:
    return CreateSupplierRelationshipHandler(
        supplier_repository=supplier_repository,
        relationship_repository=relationship_repository,
        clock=FixedClock(NOW),
        event_dispatcher=dispatcher,
    )


def test_create_relationship_for_existing_supplier_saves_and_dispatches_event() -> None:
    suppliers = InMemorySupplierRepository()
    relationships = InMemorySupplierRelationshipRepository()
    dispatcher = RecordingEventDispatcher()
    supplier_id = save_supplier(suppliers)
    organization_id = InternalOrganizationId("ORG-A")
    handler = make_handler(suppliers, relationships, dispatcher)

    result = handler.handle(
        CreateSupplierRelationship(
            supplier_id=supplier_id,
            organization_id=organization_id,
        )
    )

    loaded = relationships.get(result.relationship_id)
    assert loaded is not None
    assert loaded.supplier_id == supplier_id
    assert loaded.organization_id == organization_id
    assert loaded.stage is SupplierLifecycleStage.DISCOVERED

    assert len(dispatcher.events) == 1
    event = dispatcher.events[0]
    assert isinstance(event, SupplierRelationshipCreated)
    assert event.relationship_id == result.relationship_id
    assert event.supplier_id == supplier_id
    assert event.organization_id == organization_id
    assert event.occurred_at == NOW


def test_create_relationship_requires_existing_supplier() -> None:
    suppliers = InMemorySupplierRepository()
    relationships = InMemorySupplierRelationshipRepository()
    dispatcher = RecordingEventDispatcher()
    handler = make_handler(suppliers, relationships, dispatcher)

    with pytest.raises(SupplierNotFound):
        handler.handle(
            CreateSupplierRelationship(
                supplier_id=SupplierId.new(),
                organization_id=InternalOrganizationId("ORG-A"),
            )
        )

    assert dispatcher.events == []


def test_duplicate_supplier_organization_relationship_is_rejected() -> None:
    suppliers = InMemorySupplierRepository()
    relationships = InMemorySupplierRelationshipRepository()
    dispatcher = RecordingEventDispatcher()
    supplier_id = save_supplier(suppliers)
    organization_id = InternalOrganizationId("ORG-A")
    handler = make_handler(suppliers, relationships, dispatcher)
    command = CreateSupplierRelationship(
        supplier_id=supplier_id,
        organization_id=organization_id,
    )
    handler.handle(command)
    dispatcher.events.clear()

    with pytest.raises(RelationshipAlreadyExists):
        handler.handle(command)

    assert dispatcher.events == []


def test_same_supplier_can_have_relationships_with_two_organizations() -> None:
    suppliers = InMemorySupplierRepository()
    relationships = InMemorySupplierRelationshipRepository()
    dispatcher = RecordingEventDispatcher()
    supplier_id = save_supplier(suppliers)
    handler = make_handler(suppliers, relationships, dispatcher)

    first = handler.handle(
        CreateSupplierRelationship(
            supplier_id=supplier_id,
            organization_id=InternalOrganizationId("ORG-A"),
        )
    )
    second = handler.handle(
        CreateSupplierRelationship(
            supplier_id=supplier_id,
            organization_id=InternalOrganizationId("ORG-B"),
        )
    )

    assert first.relationship_id != second.relationship_id
    assert (
        relationships.find_for_supplier_and_organization(
            supplier_id,
            InternalOrganizationId("ORG-A"),
        )
        is not None
    )
    assert (
        relationships.find_for_supplier_and_organization(
            supplier_id,
            InternalOrganizationId("ORG-B"),
        )
        is not None
    )
    assert len(dispatcher.events) == 2
