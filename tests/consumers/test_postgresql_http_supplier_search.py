"""A4-03: canonical HTTP Supplier search against the real PostgreSQL service.

The same PySRMKit SQL runtime is accessed directly and through FastAPI.
All observations are made against PostgreSQL, not SQLite or mock adapters.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from typing import Protocol, cast

import pytest
from examples.http_api import create_app
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy.engine import Engine

from pysrmkit import PySRMKit
from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.schema import load_persistence_metadata
from pysrmkit.public import ExternalIdentifierInput

pytestmark = pytest.mark.postgresql


class HttpConsumer(Protocol):
    def get(self, url: str, *, params: dict[str, int | str]) -> Response: ...


@pytest.fixture
def runtime() -> Iterator[tuple[PySRMKit, Engine]]:
    """Clean schema and separate SQL sessions for each canonical HTTP scenario."""
    url = os.environ.get("PYSRMKIT_POSTGRESQL_TEST_URL")
    if url is None:
        pytest.skip("PYSRMKIT_POSTGRESQL_TEST_URL is not configured")

    engine = create_persistence_engine(url)
    metadata = load_persistence_metadata()
    metadata.drop_all(engine)
    metadata.create_all(engine)
    try:
        yield PySRMKit.sql(engine), engine
    finally:
        metadata.drop_all(engine)
        engine.dispose()


def _seed(srm: PySRMKit) -> None:
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


@pytest.mark.parametrize(
    "options",
    (
        {"query": "aTlAs", "sort_order": "asc", "offset": 0, "limit": 100},
        {"query": "aTlAs", "sort_order": "desc", "offset": 1, "limit": 1},
        {"query": " aTlAs ", "country_code": " fr ", "supplier_type": " MANUFACTURER "},
        {"country_code": "FR", "sort_order": "desc", "offset": 0, "limit": 2},
        {"query": "missing", "offset": 10, "limit": 1},
        {"offset": 0, "limit": 2},
    ),
    ids=(
        "name-ascending",
        "name-descending-paged",
        "combined-filters",
        "country-descending",
        "missing-result",
        "unfiltered-sort",
    ),
)
def test_postgresql_http_equals_python_query_contract(
    runtime: tuple[PySRMKit, Engine], options: dict[str, int | str]
) -> None:
    srm, _engine = runtime
    _seed(srm)
    # Intentionally dynamic: HTTP query parameters exercise public input validation.
    expected = srm.suppliers.search(**options)  # type: ignore[arg-type]
    before = srm.suppliers.list()
    with TestClient(create_app(srm)) as raw_client:
        client = cast(HttpConsumer, raw_client)
        response = client.get("/suppliers/search", params=options)

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == expected.total
    assert payload["offset"] == expected.offset
    assert payload["limit"] == (expected.limit if "limit" in options else 25)
    assert [item["supplier_id"] for item in payload["items"]] == [
        str(item.supplier_id) for item in expected.items
    ]
    assert [item["legal_name"] for item in payload["items"]] == [
        item.legal_name for item in expected.items
    ]
    assert srm.suppliers.list() == before


def test_postgresql_canonical_search_is_not_legacy_full_text(
    runtime: tuple[PySRMKit, Engine],
) -> None:
    srm, _engine = runtime
    _seed(srm)
    with TestClient(create_app(srm)) as raw_client:
        client = cast(HttpConsumer, raw_client)
        canonical_type = client.get("/suppliers/search", params={"query": "SERVICE"})
        legacy_type = client.get("/suppliers", params={"query": "SERVICE"})
        canonical_id = client.get("/suppliers/search", params={"query": "ERP-654"})
        legacy_id = client.get("/suppliers", params={"query": "ERP-654"})
    assert canonical_type.status_code == legacy_type.status_code == 200
    assert canonical_type.json()["total"] == 0
    assert legacy_type.json()["total"] == 2
    assert canonical_id.status_code == legacy_id.status_code == 200
    assert canonical_id.json()["total"] == 0
    assert legacy_id.json()["total"] == 1


@pytest.mark.parametrize(
    "options",
    (
        {"country_code": "FRA"},
        {"country_code": ""},
        {"limit": 0},
        {"limit": 101},
        {"offset": -1},
        {"sort_by": "updated_at"},
        {"sort_order": "random"},
    ),
)
def test_postgresql_canonical_http_validates_without_mutation(
    runtime: tuple[PySRMKit, Engine], options: dict[str, int | str]
) -> None:
    srm, _engine = runtime
    _seed(srm)
    before = srm.suppliers.list()
    with TestClient(create_app(srm)) as raw_client:
        client = cast(HttpConsumer, raw_client)
        response = client.get("/suppliers/search", params=options)
    assert response.status_code == 422
    assert srm.suppliers.list() == before


def test_postgresql_canonical_http_survives_runtime_recomposition(
    runtime: tuple[PySRMKit, Engine],
) -> None:
    srm, engine = runtime
    _seed(srm)
    expected = srm.suppliers.search(query="atlas", limit=25)

    # A new composition root uses fresh SQLAlchemy sessions, and reads
    # only committed data from PostgreSQL. No in-process cache dependence.
    reloaded = PySRMKit.sql(engine)
    with TestClient(create_app(reloaded)) as raw_client:
        client = cast(HttpConsumer, raw_client)
        result = client.get("/suppliers/search", params={"query": "atlas", "limit": 25})

    assert result.status_code == 200
    assert result.json()["total"] == expected.total == 2
    assert [item["supplier_id"] for item in result.json()["items"]] == [
        str(item.supplier_id) for item in expected.items
    ]


def test_postgresql_canonical_http_treats_wildcards_as_literals(
    runtime: tuple[PySRMKit, Engine],
) -> None:
    srm, _engine = runtime
    srm.suppliers.register(legal_name="One 100% Supplier")
    srm.suppliers.register(legal_name="One_name Supplier")
    srm.suppliers.register(legal_name="Regular Supplier")
    with TestClient(create_app(srm)) as raw_client:
        client = cast(HttpConsumer, raw_client)
        percent = client.get("/suppliers/search", params={"query": "%"})
        underscore = client.get("/suppliers/search", params={"query": "_"})
    assert percent.status_code == underscore.status_code == 200
    assert [v["legal_name"] for v in percent.json()["items"]] == ["One 100% Supplier"]
    assert [v["legal_name"] for v in underscore.json()["items"]] == [
        "One_name Supplier"
    ]
