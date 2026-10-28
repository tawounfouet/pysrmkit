"""In-memory implementation of the SupplierRepository port."""

from __future__ import annotations

from dataclasses import dataclass

from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import ExternalIdentifier, SupplierId, SupplierIdentity
from pysrmkit.ports.queries.supplier import SupplierPage


@dataclass(frozen=True, slots=True)
class _StoredSupplier:
    supplier_id: SupplierId
    identity: SupplierIdentity
    external_identifiers: tuple[ExternalIdentifier, ...]


class InMemorySupplierRepository:
    """Persistence-like in-memory Supplier repository for local execution and tests."""

    def __init__(self) -> None:
        self._suppliers: dict[SupplierId, _StoredSupplier] = {}

    def get(self, supplier_id: SupplierId) -> Supplier | None:
        stored = self._suppliers.get(supplier_id)
        if stored is None:
            return None
        return self._restore(stored)

    def save(self, supplier: Supplier) -> None:
        self._suppliers[supplier.id] = _StoredSupplier(
            supplier_id=supplier.id,
            identity=supplier.identity,
            external_identifiers=supplier.external_identifiers,
        )

    def find_by_external_identifier(
        self,
        identifier: ExternalIdentifier,
    ) -> Supplier | None:
        for stored in self._suppliers.values():
            if identifier in stored.external_identifiers:
                return self._restore(stored)
        return None

    def list_suppliers(self, *, offset: int, limit: int) -> SupplierPage:
        stored_suppliers = sorted(
            self._suppliers.values(),
            key=lambda stored: stored.supplier_id.value,
        )
        return SupplierPage(
            suppliers=tuple(
                self._restore(stored) for stored in stored_suppliers[offset : offset + limit]
            ),
            total=len(stored_suppliers),
        )

    @staticmethod
    def _restore(stored: _StoredSupplier) -> Supplier:
        return Supplier.reconstitute(
            supplier_id=stored.supplier_id,
            identity=stored.identity,
            external_identifiers=stored.external_identifiers,
        )
