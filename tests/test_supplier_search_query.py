"""Contract tests for the transport-independent Supplier search query DTO."""

from dataclasses import FrozenInstanceError
from typing import Literal, cast

import pytest

from pysrmkit.public._queries import SearchSuppliersQuery


def test_search_query_defaults_are_stable_and_bounded() -> None:
    query = SearchSuppliersQuery()

    assert query.query is None
    assert query.country_code is None
    assert query.supplier_type is None
    assert query.sort_by == "legal_name"
    assert query.sort_order == "asc"
    assert query.offset == 0
    assert query.limit == 100


def test_search_query_normalizes_optional_text_and_country() -> None:
    query = SearchSuppliersQuery(
        query="  Asteria  ",
        country_code=" fr ",
        supplier_type="  MANUFACTURER  ",
        sort_order="desc",
        offset=25,
        limit=25,
    )

    assert query.query == "Asteria"
    assert query.country_code == "FR"
    assert query.supplier_type == "MANUFACTURER"
    assert query.sort_order == "desc"
    assert query.offset == 25
    assert query.limit == 25


def test_search_query_treats_blank_optional_text_as_no_filter() -> None:
    query = SearchSuppliersQuery(query=" \t ", supplier_type="  ")

    assert query.query is None
    assert query.supplier_type is None


def test_search_query_preserves_case_and_accents_pending_adapter_contract() -> None:
    query = SearchSuppliersQuery(query="  Café Étoile  ", supplier_type="Local")

    assert query.query == "Café Étoile"
    assert query.supplier_type == "Local"


def test_search_query_is_immutable() -> None:
    query = SearchSuppliersQuery(query="Asteria")

    with pytest.raises(FrozenInstanceError):
        query.query = "Changed"  # type: ignore[misc]


@pytest.mark.parametrize("country_code", ["", "F", "FRA", "F1"])
def test_search_query_rejects_invalid_country_codes(country_code: str) -> None:
    with pytest.raises(ValueError, match="CountryCode"):
        SearchSuppliersQuery(country_code=country_code)


@pytest.mark.parametrize("sort_by", ["trading_name", "supplier_id", "updated_at"])
def test_search_query_rejects_unsupported_sort_fields(sort_by: str) -> None:
    with pytest.raises(ValueError, match="sort_by"):
        SearchSuppliersQuery(sort_by=cast(Literal["legal_name"], sort_by))


@pytest.mark.parametrize("sort_order", ["", "ASC", "descending", "random"])
def test_search_query_rejects_unsupported_sort_orders(sort_order: str) -> None:
    with pytest.raises(ValueError, match="sort_order"):
        SearchSuppliersQuery(sort_order=cast(Literal["asc", "desc"], sort_order))


@pytest.mark.parametrize("offset", [-1, -25])
def test_search_query_rejects_negative_offsets(offset: int) -> None:
    with pytest.raises(ValueError, match="offset must be non-negative"):
        SearchSuppliersQuery(offset=offset)


@pytest.mark.parametrize("limit", [0, -1, 101, 1000])
def test_search_query_rejects_out_of_range_limits(limit: int) -> None:
    with pytest.raises(ValueError, match="limit"):
        SearchSuppliersQuery(limit=limit)


def test_search_query_accepts_pagination_boundaries() -> None:
    assert SearchSuppliersQuery(offset=0, limit=1).limit == 1
    assert SearchSuppliersQuery(offset=200, limit=100).offset == 200


def test_search_query_rejects_boolean_pagination_values() -> None:
    with pytest.raises(TypeError, match="offset must be an integer"):
        SearchSuppliersQuery(offset=cast(int, True))
    with pytest.raises(TypeError, match="limit must be an integer"):
        SearchSuppliersQuery(limit=cast(int, False))


def test_search_query_rejects_non_string_filters() -> None:
    with pytest.raises(TypeError, match="query must be a string"):
        SearchSuppliersQuery(query=cast(str, 123))
    with pytest.raises(TypeError, match="country_code must be a string"):
        SearchSuppliersQuery(country_code=cast(str, 123))
    with pytest.raises(TypeError, match="supplier_type must be a string"):
        SearchSuppliersQuery(supplier_type=cast(str, 123))
