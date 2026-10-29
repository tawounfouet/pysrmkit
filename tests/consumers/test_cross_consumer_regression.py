"""A4-05 cross-consumer regression matrix for pagination, errors and isolation.

Canonical Python and HTTP share a port contract; legacy HTTP retains UUID
listing/search semantics. These tests intentionally compare both surfaces.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol, cast

import pytest
from examples.http_api import create_app
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import create_engine

from pysrmkit import PySRMKit
from pysrmkit.adapters.sqlalchemy.schema import load_persistence_metadata


class HttpConsumer(Protocol):
    def get(self, url: str, *, params: dict[str, int | str]) -> Response: ...


@pytest.fixture(params=("memory", "sqlite"))
def isolated_runtimes(
    request: pytest.FixtureRequest, tmp_path: Path
) -> Iterator[tuple[PySRMKit, PySRMKit]]:
    """Two independent composition roots must not leak Supplier records."""
    if request.param == "memory":
        yield PySRMKit.in_memory(), PySRMKit.in_memory()
        return

    first = create_engine(f"sqlite+pysqlite:///{tmp_path / 'first.db'}")
    second = create_engine(f"sqlite+pysqlite:///{tmp_path / 'second.db'}")
    metadata = load_persistence_metadata()
    metadata.create_all(first)
    metadata.create_all(second)
    try:
        yield PySRMKit.sql(first), PySRMKit.sql(second)
    finally:
        first.dispose()
        second.dispose()


def test_cross_consumer_data_isolation(
    isolated_runtimes: tuple[PySRMKit, PySRMKit],
) -> None:
    first, second = isolated_runtimes
    first.suppliers.register(legal_name="Atlas First Tenant", country_code="FR")
    second.suppliers.register(legal_name="Boreal Second Tenant", country_code="DE")

    with TestClient(create_app(first)) as first_raw, TestClient(create_app(second)) as second_raw:
        first_http = cast(HttpConsumer, first_raw)
        second_http = cast(HttpConsumer, second_raw)
        first_canonical = first_http.get("/suppliers/search", params={"limit": 100})
        second_canonical = second_http.get("/suppliers/search", params={"limit": 100})
        first_legacy = first_http.get("/suppliers", params={"limit": 100})
        second_legacy = second_http.get("/suppliers", params={"limit": 100})

    for response in (first_canonical, first_legacy):
        assert response.status_code == 200
        assert [item["legal_name"] for item in response.json()["items"]] == [
            "Atlas First Tenant"
        ]
        assert response.json()["total"] == 1
    for response in (second_canonical, second_legacy):
        assert response.status_code == 200
        assert [item["legal_name"] for item in response.json()["items"]] == [
            "Boreal Second Tenant"
        ]
        assert response.json()["total"] == 1
    assert first.suppliers.search(query="Boreal").total == 0
    assert second.suppliers.search(query="Atlas").total == 0


@pytest.mark.parametrize("offset,limit", ((0, 1), (1, 1), (0, 2), (3, 1), (99, 2)))
def test_canonical_http_page_boundaries_match_python(
    isolated_runtimes: tuple[PySRMKit, PySRMKit], offset: int, limit: int
) -> None:
    first, second = isolated_runtimes
    for name in ("Zeta Parts", "Atlas Services", "Boreal Manufacturing"):
        first.suppliers.register(legal_name=name)
    second.suppliers.register(legal_name="Other Store")

    expected = first.suppliers.search(offset=offset, limit=limit)
    previous_first = first.suppliers.list()
    previous_second = second.suppliers.list()
    with TestClient(create_app(first)) as raw_client:
        client = cast(HttpConsumer, raw_client)
        response = client.get("/suppliers/search", params={"offset": offset, "limit": limit})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == expected.total == 3
    assert payload["offset"] == offset
    assert payload["limit"] == limit
    assert [item["supplier_id"] for item in payload["items"]] == [
        str(item.supplier_id) for item in expected.items
    ]
    assert first.suppliers.list() == previous_first
    assert second.suppliers.list() == previous_second


@pytest.mark.parametrize(
    "options",
    (
        {"offset": -1},
        {"limit": 0},
        {"limit": 101},
        {"country_code": "BAD"},
        {"sort_by": "supplier_id"},
        {"sort_order": "DESC"},
    ),
)
def test_invalid_canonical_query_does_not_mutate_legacy_consumer(
    isolated_runtimes: tuple[PySRMKit, PySRMKit], options: dict[str, int | str]
) -> None:
    first, second = isolated_runtimes
    first.suppliers.register(legal_name="Atlas Reliable")
    second.suppliers.register(legal_name="Boreal Independent")
    before_first = first.suppliers.list()
    before_second = second.suppliers.list()
    with TestClient(create_app(first)) as raw_client:
        client = cast(HttpConsumer, raw_client)
        invalid = client.get("/suppliers/search", params=options)
        legacy = client.get("/suppliers", params={"limit": 100})

    assert invalid.status_code == 422
    assert legacy.status_code == 200
    assert legacy.json()["total"] == 1
    assert legacy.json()["items"][0]["legal_name"] == "Atlas Reliable"
    assert first.suppliers.list() == before_first
    assert second.suppliers.list() == before_second


def test_canonical_and_legacy_search_keep_distinct_filtering_and_sorting(
    isolated_runtimes: tuple[PySRMKit, PySRMKit],
) -> None:
    first, _second = isolated_runtimes
    first.suppliers.register(legal_name="Zeta Components", supplier_type="SERVICE")
    first.suppliers.register(legal_name="Atlas Components", supplier_type="SERVICE")
    first.suppliers.register(legal_name="Boreal Logistics", supplier_type="MANUFACTURER")

    with TestClient(create_app(first)) as raw_client:
        client = cast(HttpConsumer, raw_client)
        canonical = client.get("/suppliers/search", params={"query": "Components"})
        legacy = client.get("/suppliers", params={"query": "Components"})
        type_search = client.get("/suppliers", params={"query": "SERVICE"})
        canonical_type = client.get("/suppliers/search", params={"query": "SERVICE"})

    assert canonical.status_code == legacy.status_code == 200
    assert [item["legal_name"] for item in canonical.json()["items"]] == [
        "Atlas Components",
        "Zeta Components",
    ]
    assert {item["supplier_id"] for item in legacy.json()["items"]} == {
        item["supplier_id"] for item in canonical.json()["items"]
    }
    assert type_search.json()["total"] == 2
    assert canonical_type.json()["total"] == 0
