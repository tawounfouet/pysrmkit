"""Repository contract for the Supplier Aggregate Root."""

from __future__ import annotations

from typing import Protocol

from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import ExternalIdentifier, SupplierId


class SupplierRepository(Protocol):
    """Persistence abstraction required by Supplier application use cases."""

    def get(self, supplier_id: SupplierId) -> Supplier | None: ...

    def save(self, supplier: Supplier) -> None: ...

    def find_by_external_identifier(
        self,
        identifier: ExternalIdentifier,
    ) -> Supplier | None: ...
