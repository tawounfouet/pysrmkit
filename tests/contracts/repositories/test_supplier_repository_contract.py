"""Shared behavioral contract for SupplierRepository implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime

from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import ExternalIdentifier, SupplierId, SupplierIdentity
from pysrmkit.ports.repositories.supplier import SupplierRepository

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


def make_supplier(
    *,
    legal_name: str = "ACME",
    identifier: ExternalIdentifier | None = None,
) -> Supplier:
    identifiers = () if identifier is None else (identifier,)
    return Supplier.create(
        supplier_id=SupplierId.new(),
        identity=SupplierIdentity(legal_name=legal_name),
        occurred_at=NOW,
        external_identifiers=identifiers,
    )


class SupplierRepositoryContract(ABC):
    """Behavior every SupplierRepository adapter must preserve."""

    @abstractmethod
    def make_repository(self) -> SupplierRepository:
        raise NotImplementedError

    def test_save_then_get_returns_same_logical_supplier(self) -> None:
        repository = self.make_repository()
        supplier = make_supplier()

        repository.save(supplier)
        loaded = repository.get(supplier.id)

        assert loaded is not None
        assert loaded == supplier
        assert loaded.identity == supplier.identity

    def test_unknown_id_returns_none(self) -> None:
        repository = self.make_repository()

        assert repository.get(SupplierId.new()) is None

    def test_updated_state_survives_explicit_save_and_reload(self) -> None:
        repository = self.make_repository()
        supplier = make_supplier()
        repository.save(supplier)

        loaded = repository.get(supplier.id)
        assert loaded is not None
        loaded.update_identity(SupplierIdentity(legal_name="ACME Updated"))
        repository.save(loaded)

        reloaded = repository.get(supplier.id)
        assert reloaded is not None
        assert reloaded.identity.legal_name == "ACME Updated"

    def test_find_by_external_identifier_returns_matching_supplier(self) -> None:
        repository = self.make_repository()
        identifier = ExternalIdentifier(kind="SIREN", value="123456789")
        supplier = make_supplier(identifier=identifier)
        repository.save(supplier)

        loaded = repository.find_by_external_identifier(identifier)

        assert loaded is not None
        assert loaded.id == supplier.id

    def test_unknown_external_identifier_returns_none(self) -> None:
        repository = self.make_repository()

        assert (
            repository.find_by_external_identifier(
                ExternalIdentifier(kind="SIREN", value="000000000")
            )
            is None
        )

    def test_suppliers_are_isolated(self) -> None:
        repository = self.make_repository()
        first = make_supplier(legal_name="First")
        second = make_supplier(legal_name="Second")
        repository.save(first)
        repository.save(second)

        loaded_first = repository.get(first.id)
        loaded_second = repository.get(second.id)

        assert loaded_first is not None
        assert loaded_second is not None
        assert loaded_first.identity.legal_name == "First"
        assert loaded_second.identity.legal_name == "Second"

    def test_unsaved_mutation_does_not_leak_into_repository_state(self) -> None:
        repository = self.make_repository()
        supplier = make_supplier()
        repository.save(supplier)

        loaded = repository.get(supplier.id)
        assert loaded is not None
        loaded.update_identity(SupplierIdentity(legal_name="Not Saved"))

        unchanged = repository.get(supplier.id)
        assert unchanged is not None
        assert unchanged.identity.legal_name == "ACME"
