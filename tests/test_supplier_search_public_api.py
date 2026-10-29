"""A2-04 public Supplier search facade and compatibility tests."""

from typing import Literal, cast

import pytest

from pysrmkit import PySRMKit
from pysrmkit.adapters.memory.supplier_repository import InMemorySupplierRepository
from pysrmkit.application.supplier.commands import RegisterSupplier
from pysrmkit.application.supplier.results import RegisterSupplierResult
from pysrmkit.domain.supplier.value_objects import SupplierId
from pysrmkit.public._queries import SearchSuppliersQuery
from pysrmkit.public.capabilities import SuppliersAPI
from pysrmkit.public.query_handlers import GetSupplierHandler, ListSuppliersHandler
from pysrmkit.public.views import SupplierPageView


class _RegisterSupplierStub:
    def handle(self, command: RegisterSupplier, /) -> RegisterSupplierResult:
        del command
        return RegisterSupplierResult(supplier_id=SupplierId.new())


class _SearchSuppliersSpy:
    def __init__(self) -> None:
        self.calls: list[SearchSuppliersQuery] = []

    def handle(self, query: SearchSuppliersQuery, /) -> SupplierPageView:
        self.calls.append(query)
        return SupplierPageView(items=(), total=13, offset=query.offset, limit=query.limit)


def _build_suppliers_api(spy: _SearchSuppliersSpy) -> SuppliersAPI:
    repository = InMemorySupplierRepository()
    return SuppliersAPI(
        register_supplier=_RegisterSupplierStub(),
        get_supplier=GetSupplierHandler(repository),
        list_suppliers=ListSuppliersHandler(repository),
        search_suppliers=spy,
    )


def test_search_forwards_validated_query_to_injected_handler() -> None:
    spy = _SearchSuppliersSpy()
    api = _build_suppliers_api(spy)

    result = api.search(
        query="  Asteria  ",
        country_code=" fr ",
        supplier_type="  MANUFACTURER  ",
        sort_order="desc",
        offset=25,
        limit=25,
    )

    assert result == SupplierPageView(items=(), total=13, offset=25, limit=25)
    assert spy.calls == [
        SearchSuppliersQuery(
            query="Asteria",
            country_code="FR",
            supplier_type="MANUFACTURER",
            sort_by="legal_name",
            sort_order="desc",
            offset=25,
            limit=25,
        )
    ]


def test_search_defaults_preserve_existing_pagination_semantics() -> None:
    spy = _SearchSuppliersSpy()
    api = _build_suppliers_api(spy)

    result = api.search()

    assert result.total == 13
    assert result.offset == 0
    assert result.limit == 100
    assert spy.calls == [SearchSuppliersQuery()]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"offset": -1}, "offset must be non-negative"),
        ({"limit": 0}, "limit must be positive"),
        ({"limit": 101}, "limit must not exceed 100"),
        ({"country_code": "FRA"}, "CountryCode"),
    ],
)
def test_search_rejects_invalid_inputs_before_calling_handler(
    kwargs: dict[str, object],
    message: str,
) -> None:
    spy = _SearchSuppliersSpy()
    api = _build_suppliers_api(spy)

    # The kwargs are intentionally dynamic to exercise runtime validation.
    with pytest.raises(ValueError, match=message):
        api.search(**kwargs)  # type: ignore[arg-type]

    assert spy.calls == []


def test_search_rejects_unsupported_sort_without_dispatch() -> None:
    spy = _SearchSuppliersSpy()
    api = _build_suppliers_api(spy)

    with pytest.raises(ValueError, match="sort_by"):
        api.search(sort_by=cast(Literal["legal_name"], "created_at"))
    with pytest.raises(ValueError, match="sort_order"):
        api.search(sort_order=cast(Literal["asc", "desc"], "random"))

    assert spy.calls == []


def test_unconfigured_search_is_explicit_and_legacy_listing_still_works() -> None:
    srm = PySRMKit.in_memory()
    srm.suppliers.register(legal_name="Legacy Supplier")

    result = srm.suppliers.list()

    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].legal_name == "Legacy Supplier"
    with pytest.raises(NotImplementedError, match="Supplier search is not configured"):
        srm.suppliers.search()
