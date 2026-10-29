"""Read-oriented Supplier query contracts."""

from dataclasses import dataclass
from typing import Literal, Protocol

from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import CountryCode


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


class SupplierSearchService(Protocol):
    """Optional Supplier discovery port, independent from basic listing.

    Design concepts:
        - Interface Segregation: existing list-only adapters remain valid.
        - Dependency Inversion: callers rely on a typed capability contract.
        - Query Service: discovery does not change domain state.

    Implementations must:
        - match query against legal_name and trading_name without case sensitivity;
        - apply country_code and supplier_type filters before pagination;
        - return total matches after filtering and before pagination;
        - sort by legal_name and break ties with SupplierId deterministically;
        - never mutate Supplier aggregates or emit Domain Events.

    Exact cross-database Unicode/accent comparison remains a qualification
    decision for A3 and must not be assumed from native SQL collations.
    """

    def search_suppliers(
        self,
        *,
        query: str | None,
        country_code: CountryCode | None,
        supplier_type: str | None,
        sort_by: Literal["legal_name"],
        sort_order: Literal["asc", "desc"],
        offset: int,
        limit: int,
    ) -> SupplierPage:
        """Return one filtered, deterministically sorted Supplier page."""
        ...
