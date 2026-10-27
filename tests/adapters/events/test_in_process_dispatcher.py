"""InProcessDomainEventDispatcher tests."""

from datetime import UTC, datetime
from uuid import uuid4

from pysrmkit.adapters.events.in_process import InProcessDomainEventDispatcher
from pysrmkit.domain.common.events import DomainEvent
from pysrmkit.domain.qualification.events import SupplierQualified
from pysrmkit.domain.qualification.value_objects import QualificationId, QualificationScope
from pysrmkit.domain.relationship.value_objects import (
    InternalOrganizationId,
    SupplierRelationshipId,
)

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


def make_event() -> SupplierQualified:
    return SupplierQualified(
        event_id=uuid4(),
        qualification_id=QualificationId.new(),
        relationship_id=SupplierRelationshipId.new(),
        scope=QualificationScope(organization_id=InternalOrganizationId("ORG-A")),
        occurred_at=NOW,
    )


def test_registered_handlers_are_called_in_registration_order() -> None:
    dispatcher = InProcessDomainEventDispatcher()
    calls: list[str] = []

    def first(event: DomainEvent) -> None:
        assert isinstance(event, SupplierQualified)
        calls.append("first")

    def second(event: DomainEvent) -> None:
        assert isinstance(event, SupplierQualified)
        calls.append("second")

    dispatcher.register(SupplierQualified, first)
    dispatcher.register(SupplierQualified, second)

    dispatcher.dispatch((make_event(),))

    assert calls == ["first", "second"]


def test_unregistered_event_is_harmless() -> None:
    dispatcher = InProcessDomainEventDispatcher()

    dispatcher.dispatch((make_event(),))
