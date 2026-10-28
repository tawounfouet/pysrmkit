"""Read-oriented Supplier query contracts."""

from dataclasses import dataclass
from typing import Protocol

from pysrmkit.domain.supplier.entities import Supplier


@dataclass(frozen=True, slots=True)
class SupplierPage:
    """One deterministic page of Supplier aggregates."""

    suppliers: tuple[Supplier, ...]
    total: int


class SupplierQueryService(Protocol):
    """Persistence-agnostic Supplier listing contract."""

    def list_suppliers(self, *, offset: int, limit: int) -> SupplierPage:
        """Return a bounded Supplier page and the complete result count."""
        ...
