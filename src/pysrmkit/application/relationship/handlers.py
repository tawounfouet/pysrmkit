"""Handlers orchestrating Supplier Relationship application use cases."""

from __future__ import annotations

from pysrmkit.application.relationship.commands import CreateSupplierRelationship
from pysrmkit.application.relationship.errors import RelationshipAlreadyExists, SupplierNotFound
from pysrmkit.application.relationship.results import CreateSupplierRelationshipResult
from pysrmkit.domain.relationship.entities import SupplierRelationship
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId
from pysrmkit.ports.clock import Clock
from pysrmkit.ports.events import DomainEventDispatcher
from pysrmkit.ports.repositories.relationship import SupplierRelationshipRepository
from pysrmkit.ports.repositories.supplier import SupplierRepository


class CreateSupplierRelationshipHandler:
    """Application orchestration for Supplier/organization relationship creation."""

    def __init__(
        self,
        *,
        supplier_repository: SupplierRepository,
        relationship_repository: SupplierRelationshipRepository,
        clock: Clock,
        event_dispatcher: DomainEventDispatcher,
    ) -> None:
        self._supplier_repository = supplier_repository
        self._relationship_repository = relationship_repository
        self._clock = clock
        self._event_dispatcher = event_dispatcher

    def handle(
        self,
        command: CreateSupplierRelationship,
    ) -> CreateSupplierRelationshipResult:
        supplier = self._supplier_repository.get(command.supplier_id)
        if supplier is None:
            raise SupplierNotFound(f"Supplier {command.supplier_id} does not exist")

        existing = self._relationship_repository.find_for_supplier_and_organization(
            command.supplier_id,
            command.organization_id,
        )
        if existing is not None:
            raise RelationshipAlreadyExists(
                "Relationship already exists for this Supplier and internal organization"
            )

        relationship = SupplierRelationship.create(
            relationship_id=SupplierRelationshipId.new(),
            supplier_id=command.supplier_id,
            organization_id=command.organization_id,
            occurred_at=self._clock.now(),
        )
        self._relationship_repository.save(relationship)
        self._event_dispatcher.dispatch(relationship.pull_events())

        return CreateSupplierRelationshipResult(relationship_id=relationship.id)
