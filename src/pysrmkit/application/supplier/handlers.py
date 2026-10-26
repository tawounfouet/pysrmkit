"""Handlers orchestrating Supplier application use cases."""

from __future__ import annotations

from pysrmkit.application.supplier.commands import ExternalIdentifierInput, RegisterSupplier
from pysrmkit.application.supplier.results import RegisterSupplierResult
from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.errors import DuplicateExternalIdentifier
from pysrmkit.domain.supplier.value_objects import (
    CountryCode,
    ExternalIdentifier,
    SupplierId,
    SupplierIdentity,
)
from pysrmkit.ports.clock import Clock
from pysrmkit.ports.events import DomainEventDispatcher
from pysrmkit.ports.repositories.supplier import SupplierRepository


class RegisterSupplierHandler:
    """Application orchestration for canonical Supplier registration."""

    def __init__(
        self,
        *,
        repository: SupplierRepository,
        clock: Clock,
        event_dispatcher: DomainEventDispatcher,
    ) -> None:
        self._repository = repository
        self._clock = clock
        self._event_dispatcher = event_dispatcher

    def handle(self, command: RegisterSupplier) -> RegisterSupplierResult:
        country = CountryCode(command.country_code) if command.country_code is not None else None
        identity = SupplierIdentity(
            legal_name=command.legal_name,
            trading_name=command.trading_name,
            supplier_type=command.supplier_type,
            country=country,
        )
        identifiers = tuple(
            self._external_identifier(item) for item in command.external_identifiers
        )

        for identifier in identifiers:
            existing = self._repository.find_by_external_identifier(identifier)
            if existing is not None:
                raise DuplicateExternalIdentifier(
                    f"External identifier {identifier.kind}:{identifier.value} is already assigned"
                )

        supplier = Supplier.create(
            supplier_id=SupplierId.new(),
            identity=identity,
            occurred_at=self._clock.now(),
            external_identifiers=identifiers,
        )
        self._repository.save(supplier)
        self._event_dispatcher.dispatch(supplier.pull_events())
        return RegisterSupplierResult(supplier_id=supplier.id)

    @staticmethod
    def _external_identifier(item: ExternalIdentifierInput) -> ExternalIdentifier:
        jurisdiction = (
            CountryCode(item.jurisdiction_code) if item.jurisdiction_code is not None else None
        )
        return ExternalIdentifier(
            kind=item.kind,
            value=item.value,
            source_system=item.source_system,
            jurisdiction=jurisdiction,
        )
