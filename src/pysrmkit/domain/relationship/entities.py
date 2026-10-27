"""SupplierRelationship Aggregate Root."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import uuid4

from pysrmkit.domain.common.events import DomainEvent
from pysrmkit.domain.relationship.errors import InvalidLifecycleTransition
from pysrmkit.domain.relationship.events import (
    SupplierInvited,
    SupplierOnboardingStarted,
    SupplierRelationshipCreated,
)
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierLifecycleStage,
    SupplierRelationshipId,
)
from pysrmkit.domain.supplier.value_objects import SupplierId


def _domain_event_list() -> list[DomainEvent]:
    return []


@dataclass(slots=True, eq=False)
class SupplierRelationship:
    """Association Aggregate between a canonical Supplier and an internal organization."""

    relationship_id: SupplierRelationshipId
    supplier_id: SupplierId
    organization_id: InternalOrganizationId
    _stage: SupplierLifecycleStage = field(repr=False)
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
            _stage=SupplierLifecycleStage.DISCOVERED,
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
        stage: SupplierLifecycleStage = SupplierLifecycleStage.DISCOVERED,
    ) -> Self:
        return cls(
            relationship_id=relationship_id,
            supplier_id=supplier_id,
            organization_id=organization_id,
            _stage=stage,
        )

    @property
    def id(self) -> SupplierRelationshipId:
        return self.relationship_id

    @property
    def stage(self) -> SupplierLifecycleStage:
        return self._stage

    def invite(self, *, occurred_at: datetime) -> None:
        self._require_stage(
            allowed=(SupplierLifecycleStage.DISCOVERED, SupplierLifecycleStage.PROSPECTIVE),
            target=SupplierLifecycleStage.INVITED,
        )
        self._stage = SupplierLifecycleStage.INVITED
        self._record(
            SupplierInvited(
                event_id=uuid4(),
                relationship_id=self.id,
                supplier_id=self.supplier_id,
                occurred_at=occurred_at,
            )
        )

    def start_onboarding(self, *, occurred_at: datetime) -> None:
        self._require_stage(
            allowed=(SupplierLifecycleStage.INVITED,),
            target=SupplierLifecycleStage.ONBOARDING,
        )
        self._stage = SupplierLifecycleStage.ONBOARDING
        self._record(
            SupplierOnboardingStarted(
                event_id=uuid4(),
                relationship_id=self.id,
                occurred_at=occurred_at,
            )
        )

    def pull_events(self) -> tuple[DomainEvent, ...]:
        events = tuple(self._events)
        self._events.clear()
        return events

    def _require_stage(
        self,
        *,
        allowed: tuple[SupplierLifecycleStage, ...],
        target: SupplierLifecycleStage,
    ) -> None:
        if self._stage not in allowed:
            raise InvalidLifecycleTransition(source=self._stage, target=target)

    def _record(self, event: DomainEvent) -> None:
        self._events.append(event)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, SupplierRelationship)
            and self.relationship_id == other.relationship_id
        )
