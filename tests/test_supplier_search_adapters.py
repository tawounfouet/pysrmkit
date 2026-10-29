"""A2-06 behavioral qualification for memory and SQLite Supplier search adapters.

A3 will extend these shared scenarios to PostgreSQL and Unicode policies.
"""

from collections.abc import Iterator
from dataclasses import FrozenInstanceError
from typing import Literal, cast

import pytest
from sqlalchemy import create_engine

from pysrmkit import PySRMKit, SupplierCreated
from pysrmkit.adapters.sqlalchemy.schema import load_persistence_metadata
from pysrmkit.public.views import SupplierPageView


@pytest.fixture(params=["memory", "sqlite"])
def srm(request: pytest.FixtureRequest) -> Iterator[PySRMKit]:
    """Run the same observable search behavior against both public runtimes."""
    if request.param == "memory":
        yield PySRMKit.in_memory()
        return

    engine = create_engine("sqlite+pysqlite:///:memory:")
    load_persistence_metadata().create_all(engine)
    try:
        yield PySRMKit.sql(engine)
    finally:
        engine.dispose()


def _seed(srm: PySRMKit) -> None:
    for legal_name, trading_name, supplier_type, country_code in (
        ("Atlas Components", "Atlas", "MANUFACTURER", "FR"),
        ("atlas Logistics", None, "SERVICE", "FR"),
        ("Boreal Works", "North Atlas", "MANUFACTURER", "DE"),
        ("Cedar Labs", None, "MANUFACTURER", "FR"),
        ("Atlas Components", None, "MANUFACTURER", "FR"),
        ("Percent%Works", None, "SERVICE", "FR"),
        ("Under_Score", None, "SERVICE", "FR"),
    ):
        srm.suppliers.register(
            legal_name=legal_name,
            trading_name=trading_name,
            supplier_type=supplier_type,
            country_code=country_code,
        )


def test_search_filters_before_count_and_pagination(srm: PySRMKit) -> None:
    _seed(srm)

    page = srm.suppliers.search(
        query="  ATLAS  ", country_code=" fr ", supplier_type="MANUFACTURER", limit=1
    )
    next_page = srm.suppliers.search(
        query="atlas", country_code="FR", supplier_type="MANUFACTURER", offset=1, limit=1
    )
    beyond = srm.suppliers.search(
        query="atlas", country_code="FR", supplier_type="MANUFACTURER", offset=10, limit=1
    )

    assert isinstance(page, SupplierPageView)
    assert page.total == next_page.total == beyond.total == 2
    assert (page.offset, page.limit) == (0, 1)
    assert (next_page.offset, next_page.limit) == (1, 1)
    assert len(page.items) == len(next_page.items) == 1
    assert beyond.items == ()
    assert {item.supplier_id for item in (*page.items, *next_page.items)} == {
        item.supplier_id
        for item in srm.suppliers.list().items
        if item.legal_name == "Atlas Components"
    }


def test_search_covers_trading_name_and_descending_order(srm: PySRMKit) -> None:
    _seed(srm)

    page = srm.suppliers.search(query="atlas", sort_order="desc")
    assert page.total == 4
    assert [item.legal_name for item in page.items] == [
        "Boreal Works",
        "atlas Logistics",
        "Atlas Components",
        "Atlas Components",
    ]
    atlas_ids = [
        item.supplier_id.value for item in page.items if item.legal_name == "Atlas Components"
    ]
    assert atlas_ids == sorted(atlas_ids)


def test_search_unfiltered_is_distinct_from_legacy_list_order(srm: PySRMKit) -> None:
    _seed(srm)

    page = srm.suppliers.search()
    listed = srm.suppliers.list()

    assert page.total == listed.total == 7
    assert [item.legal_name for item in page.items] == [
        "Atlas Components",
        "Atlas Components",
        "atlas Logistics",
        "Boreal Works",
        "Cedar Labs",
        "Percent%Works",
        "Under_Score",
    ]
    assert {item.supplier_id for item in page.items} == {item.supplier_id for item in listed.items}


@pytest.mark.parametrize("needle", ["Percent%", "Under_"])
def test_search_treats_sql_wildcard_characters_literally(srm: PySRMKit, needle: str) -> None:
    _seed(srm)

    page = srm.suppliers.search(query=needle)

    assert page.total == 1
    assert page.items[0].legal_name.startswith(needle)


def test_search_respects_exact_supplier_type_and_empty_filters(srm: PySRMKit) -> None:
    _seed(srm)

    page = srm.suppliers.search(query="  ", supplier_type="  ")
    assert page.total == 7
    assert srm.suppliers.search(supplier_type="SERVICE").total == 3
    assert srm.suppliers.search(supplier_type="service").total == 0
    assert srm.suppliers.search(country_code="DE").total == 1


def test_search_does_not_modify_supplier_or_public_view(srm: PySRMKit) -> None:
    created = srm.suppliers.register(legal_name="Immutable", country_code="FR")
    before = srm.suppliers.get(supplier_id=created.supplier_id)

    page = srm.suppliers.search(query="immut")
    after = srm.suppliers.get(supplier_id=created.supplier_id)

    assert page.items == (before,)
    assert after == before
    with pytest.raises(FrozenInstanceError):
        page.items[0].legal_name = "Changed"  # type: ignore[misc]


def test_search_returns_no_matches_and_partial_last_page(srm: PySRMKit) -> None:
    _seed(srm)

    missing = srm.suppliers.search(query="no-such-supplier", limit=2)
    first = srm.suppliers.search(query="atlas", limit=3)
    last = srm.suppliers.search(query="atlas", offset=3, limit=3)
    beyond = srm.suppliers.search(query="atlas", offset=4, limit=3)

    assert missing.total == 0
    assert missing.items == ()
    assert first.total == last.total == beyond.total == 4
    assert len(first.items) == 3
    assert len(last.items) == 1
    assert last.offset == 3
    assert beyond.items == ()


@pytest.mark.parametrize("sort_order", ["asc", "desc"])
def test_search_tie_break_is_stable_across_pages_and_repeated_calls(
    srm: PySRMKit, sort_order: str
) -> None:
    _seed(srm)

    order = cast(Literal["asc", "desc"], sort_order)
    first = srm.suppliers.search(query="Atlas Components", sort_order=order, limit=1)
    second = srm.suppliers.search(query="Atlas Components", sort_order=order, offset=1, limit=1)
    repeated = srm.suppliers.search(query="Atlas Components", sort_order=order, limit=2)

    ids = [item.supplier_id.value for item in (*first.items, *second.items)]
    assert first.total == second.total == repeated.total == 2
    assert ids == sorted(ids)
    assert ids == [item.supplier_id.value for item in repeated.items]


def test_search_never_changes_legacy_listing_order_or_result(srm: PySRMKit) -> None:
    _seed(srm)

    before = srm.suppliers.list(offset=1, limit=3)
    srm.suppliers.search(query="atlas", sort_order="desc", limit=2)
    after = srm.suppliers.list(offset=1, limit=3)

    assert before == after
    assert before.total == 7


def test_search_does_not_publish_domain_events(srm: PySRMKit) -> None:
    observed: list[SupplierCreated] = []
    srm.events.subscribe(SupplierCreated, observed.append)
    srm.suppliers.register(legal_name="Quiet Reads", country_code="FR")

    assert len(observed) == 1
    observed.clear()
    first = srm.suppliers.search(query="quiet")
    second = srm.suppliers.search()

    assert first.total == second.total == 1
    assert observed == []


def test_search_respects_missing_country_and_trading_name(srm: PySRMKit) -> None:
    srm.suppliers.register(legal_name="Orphan Vendor", supplier_type="SERVICE")
    srm.suppliers.register(legal_name="Scoped Vendor", country_code="FR")

    assert srm.suppliers.search(query="Orphan Vendor").total == 1
    assert srm.suppliers.search(query="Orphan Vendor", country_code="FR").total == 0
    assert srm.suppliers.search(query="Scoped Vendor", country_code="FR").total == 1
    assert srm.suppliers.search(query="Scoped Vendor", supplier_type="SERVICE").total == 0
