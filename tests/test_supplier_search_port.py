"""Qualification of the optional Supplier discovery port boundary."""

from dataclasses import FrozenInstanceError
from typing import Literal

import pytest

from pysrmkit.adapters.memory.supplier_repository import InMemorySupplierRepository
from pysrmkit.domain.supplier.value_objects import CountryCode
from pysrmkit.ports.queries.supplier import (
    SupplierPage,
    SupplierQueryService,
    SupplierSearchService,
)


class SearchPortSpy:
    """Implements only the new read port; deliberately no list_suppliers."""

    def __init__(self) -> None:
        self.last_query: str | None = None
        self.last_country: CountryCode | None = None
        self.last_supplier_type: str | None = None
        self.last_sort: tuple[str, str] | None = None
        self.last_pagination: tuple[int, int] | None = None

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
        self.last_query = query
        self.last_country = country_code
        self.last_supplier_type = supplier_type
        self.last_sort = (sort_by, sort_order)
        self.last_pagination = (offset, limit)
        return SupplierPage(suppliers=(), total=0)


def _consume_search_port(port: SupplierSearchService) -> SupplierPage:
    """Enforce the structural contract through strict static type checking."""
    return port.search_suppliers(
        query="Asteria",
        country_code=CountryCode("FR"),
        supplier_type="MANUFACTURER",
        sort_by="legal_name",
        sort_order="desc",
        offset=20,
        limit=10,
    )


def _consume_listing_port(port: SupplierQueryService) -> SupplierPage:
    return port.list_suppliers(offset=0, limit=10)


def test_supplier_search_port_is_structurally_substitutable() -> None:
    spy = SearchPortSpy()

    page = _consume_search_port(spy)

    assert page == SupplierPage(suppliers=(), total=0)
    assert spy.last_query == "Asteria"
    assert spy.last_country == CountryCode("FR")
    assert spy.last_supplier_type == "MANUFACTURER"
    assert spy.last_sort == ("legal_name", "desc")
    assert spy.last_pagination == (20, 10)


def test_existing_listing_port_remains_unchanged() -> None:
    listing_only = InMemorySupplierRepository()

    assert _consume_listing_port(listing_only) == SupplierPage(suppliers=(), total=0)
    assert "search_suppliers" not in SupplierQueryService.__dict__
    assert "list_suppliers" not in SupplierSearchService.__dict__


def test_supplier_page_contract_remains_immutable() -> None:
    page = SupplierPage(suppliers=(), total=7)

    with pytest.raises(FrozenInstanceError):
        page.total = 9  # type: ignore[misc]
