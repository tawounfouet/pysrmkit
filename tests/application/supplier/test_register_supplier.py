"""RegisterSupplier application-flow tests."""

from datetime import datetime, timezone

import pytest

from pysrmkit.adapters.clock.fixed import FixedClock
from pysrmkit.adapters.memory.supplier_repository import InMemorySupplierRepository
from pysrmkit.application.supplier.commands import ExternalIdentifierInput, RegisterSupplier
from pysrmkit.application.supplier.handlers import RegisterSupplierHandler
from pysrmkit.domain.common.events import DomainEvent
from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.errors import DuplicateExternalIdentifier, InvalidSupplierIdentity
from pysrmkit.domain.supplier.events import SupplierCreated
from pysrmkit.domain.supplier.value_objects import ExternalIdentifier, SupplierId, SupplierIdentity

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)


class RecordingEventDispatcher:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def dispatch(self, events: tuple[DomainEvent, ...]) -> None:
        self.events.extend(events)


def make_handler(
    repository: InMemorySupplierRepository,
    dispatcher: RecordingEventDispatcher,
) -> RegisterSupplierHandler:
    return RegisterSupplierHandler(
        repository=repository,
        clock=FixedClock(NOW),
        event_dispatcher=dispatcher,
    )


def test_register_supplier_creates_saves_returns_id_and_dispatches_event() -> None:
    repository = InMemorySupplierRepository()
    dispatcher = RecordingEventDispatcher()
    handler = make_handler(repository, dispatcher)

    result = handler.handle(
        RegisterSupplier(
            legal_name="ACME France",
            trading_name="ACME",
            country_code="fr",
            external_identifiers=(
                ExternalIdentifierInput(
                    kind="SIREN",
                    value="123456789",
                    jurisdiction_code="FR",
                ),
            ),
        )
    )

    loaded = repository.get(result.supplier_id)
    assert loaded is not None
    assert loaded.identity.legal_name == "ACME France"
    assert loaded.identity.country is not None
    assert loaded.identity.country.value == "FR"
    assert loaded.external_identifiers == (
        ExternalIdentifier(
            kind="SIREN",
            value="123456789",
            jurisdiction=loaded.identity.country,
        ),
    )

    assert len(dispatcher.events) == 1
    event = dispatcher.events[0]
    assert isinstance(event, SupplierCreated)
    assert event.supplier_id == result.supplier_id
    assert event.occurred_at == NOW


def test_register_supplier_rejects_cross_supplier_duplicate_external_identifier() -> None:
    repository = InMemorySupplierRepository()
    identifier = ExternalIdentifier(kind="SIREN", value="123456789")
    existing = Supplier.create(
        supplier_id=SupplierId.new(),
        identity=SupplierIdentity(legal_name="Existing Supplier"),
        occurred_at=NOW,
        external_identifiers=(identifier,),
    )
    repository.save(existing)
    dispatcher = RecordingEventDispatcher()
    handler = make_handler(repository, dispatcher)

    with pytest.raises(DuplicateExternalIdentifier):
        handler.handle(
            RegisterSupplier(
                legal_name="Conflicting Supplier",
                external_identifiers=(
                    ExternalIdentifierInput(kind="SIREN", value="123456789"),
                ),
            )
        )

    found = repository.find_by_external_identifier(identifier)
    assert found is not None
    assert found.id == existing.id
    assert dispatcher.events == []


def test_register_supplier_rejects_duplicate_identifier_inside_same_command() -> None:
    repository = InMemorySupplierRepository()
    dispatcher = RecordingEventDispatcher()
    handler = make_handler(repository, dispatcher)
    duplicate = ExternalIdentifierInput(kind="SIREN", value="123456789")

    with pytest.raises(DuplicateExternalIdentifier):
        handler.handle(
            RegisterSupplier(
                legal_name="ACME",
                external_identifiers=(duplicate, duplicate),
            )
        )

    assert dispatcher.events == []


def test_register_supplier_propagates_invalid_supplier_identity() -> None:
    handler = make_handler(InMemorySupplierRepository(), RecordingEventDispatcher())

    with pytest.raises(InvalidSupplierIdentity):
        handler.handle(RegisterSupplier(legal_name="   "))
