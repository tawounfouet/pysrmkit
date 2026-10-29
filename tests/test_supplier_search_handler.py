"""A2-05 Supplier search handler: port translation and immutable View mapping."""

from typing import Literal

from pysrmkit.adapters.memory.supplier_repository import InMemorySupplierRepository
from pysrmkit.application.supplier.commands import RegisterSupplier
from pysrmkit.application.supplier.results import RegisterSupplierResult
from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import (
    CountryCode,
    ExternalIdentifier,
    SupplierId,
    SupplierIdentity,
)
from pysrmkit.ports.queries.supplier import SupplierPage
from pysrmkit.public._queries import SearchSuppliersQuery
from pysrmkit.public.capabilities import SuppliersAPI
from pysrmkit.public.query_handlers import (
    GetSupplierHandler,
    ListSuppliersHandler,
    SearchSuppliersHandler,
)
from pysrmkit.public.views import SupplierPageView, SupplierView


class _SpySupplierSearchService:
    """Port fake - it deliberately performs no filtering or sort itself."""

    def __init__(self, result: SupplierPage) -> None:
        self.result = result
        self.calls: list[
            tuple[
                str | None,
                CountryCode | None,
                str | None,
                Literal["legal_name"],
                Literal["asc", "desc"],
                int,
                int,
            ]
        ] = []

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
        self.calls.append(
            (query, country_code, supplier_type, sort_by, sort_order, offset, limit)
        )
        return self.result


class _RegisterSupplierStub:
    def handle(self, command: RegisterSupplier, /) -> RegisterSupplierResult:
        del command
        return RegisterSupplierResult(supplier_id=SupplierId.new())


def test_search_handler_maps_port_result_into_immutable_public_views() -> None:
    identifier = ExternalIdentifier(kind="SIREN", value="123456789")
    supplier = Supplier.reconstitute(
        supplier_id=SupplierId.new(),
        identity=SupplierIdentity(
            legal_name="Asteria SAS",
            trading_name="Asteria",
            supplier_type="MANUFACTURER",
            country=CountryCode("FR"),
        ),
        external_identifiers=(identifier,),
    )
    search_port = _SpySupplierSearchService(SupplierPage(suppliers=(supplier,), total=7))
    handler = SearchSuppliersHandler(search_port)

    result = handler.handle(
        SearchSuppliersQuery(
            query="  Ast  ",
            country_code="fr",
            supplier_type="  MANUFACTURER  ",
            sort_order="desc",
            offset=20,
            limit=10,
        )
    )

    assert search_port.calls == [
        ("Ast", CountryCode("FR"), "MANUFACTURER", "legal_name", "desc", 20, 10)
    ]
    assert result == SupplierPageView(
        items=(
            SupplierView(
                supplier_id=supplier.id,
                legal_name="Asteria SAS",
                trading_name="Asteria",
                supplier_type="MANUFACTURER",
                country=CountryCode("FR"),
                external_identifiers=(identifier,),
            ),
        ),
        total=7,
        offset=20,
        limit=10,
    )
    assert supplier.pull_events() == ()


def test_search_handler_preserves_empty_page_total_and_pagination() -> None:
    search_port = _SpySupplierSearchService(SupplierPage(suppliers=(), total=42))
    handler = SearchSuppliersHandler(search_port)

    result = handler.handle(SearchSuppliersQuery(offset=50, limit=25))

    assert result == SupplierPageView(items=(), total=42, offset=50, limit=25)
    assert search_port.calls == [(None, None, None, "legal_name", "asc", 50, 25)]


def test_search_handler_composes_through_public_api_without_runtime_adapter() -> None:
    repository = InMemorySupplierRepository()
    search_port = _SpySupplierSearchService(SupplierPage(suppliers=(), total=3))
    api = SuppliersAPI(
        register_supplier=_RegisterSupplierStub(),
        get_supplier=GetSupplierHandler(repository),
        list_suppliers=ListSuppliersHandler(repository),
        search_suppliers=SearchSuppliersHandler(search_port),
    )

    page = api.search(query="  Asteria ", country_code="fr", offset=10, limit=5)

    assert page == SupplierPageView(items=(), total=3, offset=10, limit=5)
    assert search_port.calls == [
        ("Asteria", CountryCode("FR"), None, "legal_name", "asc", 10, 5)
    ]
    # The unchanged listing port can still be used independently.
    assert api.list().total == 0
