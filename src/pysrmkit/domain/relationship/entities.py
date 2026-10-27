"""SupplierRelationship Aggregate Root."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import uuid4

from pysrmkit.domain.common.events import DomainEvent
from pysrmkit.domain.relationship.events import SupplierRelationshipCreated
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId

_INITIAL_STAGE = "DISCOVERED"


def _domain_event_list() -> list[DomainEvent]:
    return []


@dataclass(slots=True, eq=False)
class SupplierRelationship:
    """Association Aggregate between a canonical Supplier and an internal organization."""

    relationship_id: SupplierRelationshipId
    supplier_id: SupplierId
    organization_id: InternalOrganizationId
    _events: list[DomainEvent] = field(default_factory=_domain_event_list, repr=False)

    @classmethod
    def create(
        cls,
        *,
        relationship_id: SupplierRelationshipId,
        supplier_id: SupplierId,
        organization_id: InternalOrganizationId,
        occurred_at: datetime,
    ) -> Self:
        relationship = cls(
            relationship_id=relationship_id,
            supplier_id=supplier_id,
            organization_id=organization_id,
        )
        relationship._record(
            SupplierRelationshipCreated(
                event_id=uuid4(),
                relationship_id=relationship_id,
                supplier_id=supplier_id,
                organization_id=organization_id,
                occurred_at=occurred_at,
            )
        )
        return relationship

    @classmethod
    def reconstitute(
        cls,
        *,
        relationship_id: SupplierRelationshipId,
        supplier_id: SupplierId,
        organization_id: InternalOrganizationId,
    ) -> Self:
        return cls(
            relationship_id=relationship_id,
            supplier_id=supplier_id,
            organization_id=organization_id,
        )

    @property
    def id(self) -> SupplierRelationshipId:
        return self.relationship_id

    @property
    def stage(self) -> str:
        """Initial lifecycle state; the lifecycle model is introduced in 0.1.0a4."""
        return _INITIAL_STAGE

    def pull_events(self) -> tuple[DomainEvent, ...]:
        events = tuple(self._events)
        self._events.clear()
        return events

    def _record(self, event: DomainEvent) -> None:
        self._events.append(event)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, SupplierRelationship)
            and self.relationship_id == other.relationship_id
        )
