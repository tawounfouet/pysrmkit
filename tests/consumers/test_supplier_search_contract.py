"""A4-01 consumer contract characterization: public facade vs FastAPI host.

This suite records both the portable overlap and the legacy HTTP differences.
It does not silently turn a mismatch into a public API guarantee.
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
from pysrmkit.public import ExternalIdentifierInput


class HttpConsumer(Protocol):
    def get(self, url: str, *, params: dict[str, int | str]) -> Response: ...


@pytest.fixture(params=("memory", "sqlite"))
def runtime(request: pytest.FixtureRequest, tmp_path: Path) -> Iterator[PySRMKit]:
    """Use the same runtime instance as both the Python and HTTP consumer."""
    if request.param == "memory":
        yield PySRMKit.in_memory()
        return

    # HTTP TestClient uses a separate thread; a file-backed SQLite database
    # keeps the same schema visible across thread-local DBAPI connections.
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'consumer.db'}")
    load_persistence_metadata().create_all(engine)
    try:
        yield PySRMKit.sql(engine)
    finally:
        engine.dispose()


def _register_corpus(srm: PySRMKit) -> None:
    srm.suppliers.register(
        legal_name="Atlas Components",
        trading_name="Atlas Parts",
        supplier_type="MANUFACTURER",
        country_code="FR",
    )
    srm.suppliers.register(
        legal_name="Boreal Supply",
        trading_name="Atlas North",
        supplier_type="SERVICE",
        country_code="DE",
    )
    srm.suppliers.register(
        legal_name="Cedar Logistics",
        supplier_type="SERVICE",
        country_code="FR",
        external_identifiers=(ExternalIdentifierInput(kind="ERP", value="ERP-654"),),
    )


def test_http_and_python_share_ascii_name_matching_for_full_result(
    runtime: PySRMKit,
) -> None:
    """Common name-only search is comparable before pagination/sort policy."""
    _register_corpus(runtime)
    expected = runtime.suppliers.search(query="aTlAs", limit=100)

    with TestClient(create_app(runtime)) as raw_client:
        client = cast(HttpConsumer, raw_client)
        response = client.get("/suppliers", params={"query": "aTlAs", "limit": 100})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == expected.total == 2
    assert {item["supplier_id"] for item in payload["items"]} == {
        str(item.supplier_id) for item in expected.items
    }
    # HTTP legacy search is ordered by list() UUIDs. The canonical API
    # sorts by legal_name; no false ordering-equivalence claim is made.


def test_unfiltered_http_list_preserves_legacy_public_listing(
    runtime: PySRMKit,
) -> None:
    _register_corpus(runtime)
    expected = runtime.suppliers.list(offset=1, limit=2)

    with TestClient(create_app(runtime)) as raw_client:
        client = cast(HttpConsumer, raw_client)
        response = client.get("/suppliers", params={"offset": 1, "limit": 2})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == expected.total == 3
    assert payload["offset"] == expected.offset == 1
    assert payload["limit"] == expected.limit == 2
    assert [item["supplier_id"] for item in payload["items"]] == [
        str(item.supplier_id) for item in expected.items
    ]


def test_http_type_search_is_broader_than_canonical_name_search(
    runtime: PySRMKit,
) -> None:
    """Known legacy behavior: HTTP query also matches Supplier Type."""
    _register_corpus(runtime)
    canonical = runtime.suppliers.search(query="SERVICE")

    with TestClient(create_app(runtime)) as raw_client:
        client = cast(HttpConsumer, raw_client)
        response = client.get("/suppliers", params={"query": "SERVICE"})

    assert canonical.total == 0
    assert response.status_code == 200
    assert response.json()["total"] == 2


def test_http_external_identifier_search_is_not_a_public_search_guarantee(
    runtime: PySRMKit,
) -> None:
    """Known legacy behavior: HTTP scans identifiers, public search does not."""
    _register_corpus(runtime)
    canonical = runtime.suppliers.search(query="ERP-654")

    with TestClient(create_app(runtime)) as raw_client:
        client = cast(HttpConsumer, raw_client)
        response = client.get("/suppliers", params={"query": "ERP-654"})

    assert canonical.total == 0
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["legal_name"] == "Cedar Logistics"


def test_legacy_http_search_paginates_after_filtering(
    runtime: PySRMKit,
) -> None:
    """The existing HTTP contract can see matches beyond list() page 100."""
    for index in range(101):
        runtime.suppliers.register(legal_name=f"Ordinary Supplier {index:03d}")
    runtime.suppliers.register(legal_name="Unique Search Target")

    with TestClient(create_app(runtime)) as raw_client:
        client = cast(HttpConsumer, raw_client)
        response = client.get(
            "/suppliers",
            params={"query": "Unique Search Target", "offset": 0, "limit": 5},
        )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["legal_name"] == "Unique Search Target"


@pytest.mark.parametrize(
    "options",
    (
        {"query": "aTlAs", "sort_order": "asc", "offset": 0, "limit": 100},
        {"query": "aTlAs", "sort_order": "desc", "offset": 1, "limit": 1},
        {
            "query": " aTlAs ",
            "country_code": " fr ",
            "supplier_type": " MANUFACTURER ",
            "offset": 0,
            "limit": 5,
        },
        {"country_code": "FR", "sort_order": "desc", "offset": 0, "limit": 2},
        {"query": "no matching supplier", "offset": 10, "limit": 1},
        {"sort_order": "asc", "offset": 0, "limit": 2},
    ),
    ids=(
        "name-ascending",
        "name-descending-paged",
        "combined-filters-normalized",
        "country-descending",
        "empty-page",
        "unfiltered-canonical-sort",
    ),
)
def test_canonical_http_search_matches_public_python_page(
    runtime: PySRMKit,
    options: dict[str, int | str],
) -> None:
    """A4-02: one search contract, with HTTP only translating to/from JSON."""
    _register_corpus(runtime)
    # Test inputs are deliberately dynamic HTTP query parameters.
    expected = runtime.suppliers.search(**options)  # type: ignore[arg-type]
    before = runtime.suppliers.list()

    with TestClient(create_app(runtime)) as raw_client:
        client = cast(HttpConsumer, raw_client)
        response = client.get("/suppliers/search", params=options)

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == expected.total
    assert payload["offset"] == expected.offset
    assert payload["limit"] == expected.limit
    assert [item["supplier_id"] for item in payload["items"]] == [
        str(supplier.supplier_id) for supplier in expected.items
    ]
    assert [item["legal_name"] for item in payload["items"]] == [
        supplier.legal_name for supplier in expected.items
    ]
    assert runtime.suppliers.list() == before


def test_canonical_http_search_keeps_legacy_type_and_identifier_semantics(
    runtime: PySRMKit,
) -> None:
    """Canonical search must not accidentally inherit legacy full-scan fields."""
    _register_corpus(runtime)
    with TestClient(create_app(runtime)) as raw_client:
        client = cast(HttpConsumer, raw_client)
        canonical_type = client.get("/suppliers/search", params={"query": "SERVICE"})
        legacy_type = client.get("/suppliers", params={"query": "SERVICE"})
        canonical_identifier = client.get("/suppliers/search", params={"query": "ERP-654"})
        legacy_identifier = client.get("/suppliers", params={"query": "ERP-654"})

    assert canonical_type.status_code == legacy_type.status_code == 200
    assert canonical_type.json()["total"] == 0
    assert legacy_type.json()["total"] == 2
    assert canonical_identifier.status_code == legacy_identifier.status_code == 200
    assert canonical_identifier.json()["total"] == 0
    assert legacy_identifier.json()["total"] == 1


@pytest.mark.parametrize(
    "options",
    (
        {"offset": -1},
        {"limit": 0},
        {"limit": 101},
        {"country_code": "FRA"},
        {"country_code": ""},
        {"sort_by": "created_at"},
        {"sort_order": "random"},
        {"query": "a" * 101},
        {"supplier_type": "S" * 101},
    ),
)
def test_canonical_http_search_rejects_invalid_parameters(
    runtime: PySRMKit,
    options: dict[str, int | str],
) -> None:
    """HTTP validation and business DTO validation converge on HTTP 422."""
    with TestClient(create_app(runtime)) as raw_client:
        client = cast(HttpConsumer, raw_client)
        response = client.get("/suppliers/search", params=options)
    assert response.status_code == 422


def test_canonical_http_search_preserves_literal_sql_wildcards(
    runtime: PySRMKit,
) -> None:
    runtime.suppliers.register(legal_name="Supplier 100% Services")
    runtime.suppliers.register(legal_name="Supplier_name")
    runtime.suppliers.register(legal_name="Supplier Standard")
    for literal in ("%", "_"):
        expected = runtime.suppliers.search(query=literal)
        with TestClient(create_app(runtime)) as raw_client:
            client = cast(HttpConsumer, raw_client)
            response = client.get("/suppliers/search", params={"query": literal})
        assert response.status_code == 200
        assert response.json()["total"] == expected.total == 1
        assert [item["supplier_id"] for item in response.json()["items"]] == [
            str(item.supplier_id) for item in expected.items
        ]
