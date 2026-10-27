"""Supplier Aggregate Root."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import uuid4

from pysrmkit.domain.common.events import DomainEvent
from pysrmkit.domain.supplier.errors import DuplicateExternalIdentifier
from pysrmkit.domain.supplier.events import SupplierCreated
from pysrmkit.domain.supplier.value_objects import ExternalIdentifier, SupplierId, SupplierIdentity


def _external_identifier_list() -> list[ExternalIdentifier]:
    return []


def _domain_event_list() -> list[DomainEvent]:
    return []


@dataclass(slots=True, eq=False)
class Supplier:
    """Aggregate Root representing the canonical supplier identity."""

    supplier_id: SupplierId
    identity: SupplierIdentity
    _external_identifiers: list[ExternalIdentifier] = field(
        default_factory=_external_identifier_list,
        repr=False,
    )
    _events: list[DomainEvent] = field(default_factory=_domain_event_list, repr=False)

    @classmethod
    def create(
        cls,
        *,
        supplier_id: SupplierId,
        identity: SupplierIdentity,
        occurred_at: datetime,
        external_identifiers: Iterable[ExternalIdentifier] = (),
    ) -> Self:
        supplier = cls(supplier_id=supplier_id, identity=identity)
        for identifier in external_identifiers:
            supplier.add_external_identifier(identifier)
        supplier._record(
            SupplierCreated(
                event_id=uuid4(),
                supplier_id=supplier_id,
                occurred_at=occurred_at,
            )
        )
        return supplier

    @classmethod
    def reconstitute(
        cls,
        *,
        supplier_id: SupplierId,
        identity: SupplierIdentity,
        external_identifiers: Iterable[ExternalIdentifier] = (),
    ) -> Self:
        supplier = cls(supplier_id=supplier_id, identity=identity)
        for identifier in external_identifiers:
            supplier.add_external_identifier(identifier)
        return supplier

    @property
    def id(self) -> SupplierId:
        return self.supplier_id

    @property
    def external_identifiers(self) -> tuple[ExternalIdentifier, ...]:
        return tuple(self._external_identifiers)

    def add_external_identifier(self, identifier: ExternalIdentifier) -> None:
        if identifier in self._external_identifiers:
            raise DuplicateExternalIdentifier(
                f"External identifier {identifier.kind}:{identifier.value} already exists"
            )
        self._external_identifiers.append(identifier)

    def update_identity(self, identity: SupplierIdentity) -> None:
        self.identity = identity

    def pull_events(self) -> tuple[DomainEvent, ...]:
        events = tuple(self._events)
        self._events.clear()
        return events

    def _record(self, event: DomainEvent) -> None:
        self._events.append(event)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Supplier) and self.supplier_id == other.supplier_id
