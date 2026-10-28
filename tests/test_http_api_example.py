"""HTTP qualification for the FastAPI consumer example."""

from typing import Protocol, cast

from examples.http_api import create_app
from fastapi.testclient import TestClient
from httpx import Response

from pysrmkit import PySRMKit


class HttpTestClient(Protocol):
    def get(self, url: str, *, params: dict[str, int | str]) -> Response: ...

    def post(self, url: str, *, json: object) -> Response: ...


def test_supplier_http_journey() -> None:
    app = create_app(PySRMKit.in_memory())

    with TestClient(app) as raw_client:
        client = cast(HttpTestClient, raw_client)
        created = client.post(
            "/suppliers",
            json={
                "legal_name": "Northwind Industrial SAS",
                "trading_name": "Northwind",
                "supplier_type": "LEGAL_ENTITY",
                "country_code": "FR",
            },
        )
        page = client.get("/suppliers", params={"offset": 0, "limit": 10})

    assert created.status_code == 201
    assert created.json()["country_code"] == "FR"
    assert page.status_code == 200
    assert page.json()["total"] == 1
    assert page.json()["items"][0]["legal_name"] == "Northwind Industrial SAS"


def test_supplier_http_pagination_is_validated() -> None:
    app = create_app(PySRMKit.in_memory())

    with TestClient(app) as raw_client:
        client = cast(HttpTestClient, raw_client)
        response = client.get("/suppliers", params={"limit": 0})

    assert response.status_code == 422


def test_supplier_http_searches_the_complete_supplier_set() -> None:
    srm = PySRMKit.in_memory()
    for index in range(101):
        srm.suppliers.register(legal_name=f"Supplier {index:03d}")
    app = create_app(srm)

    with TestClient(app) as raw_client:
        client = cast(HttpTestClient, raw_client)
        response = client.get("/suppliers", params={"query": "Supplier 100", "limit": 25})

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["legal_name"] == "Supplier 100"


def test_supplier_http_rejects_oversized_external_identifiers() -> None:
    app = create_app(PySRMKit.in_memory())

    with TestClient(app) as raw_client:
        client = cast(HttpTestClient, raw_client)
        response = client.post(
            "/suppliers",
            json={
                "legal_name": "Invalid Supplier",
                "external_identifiers": [{"kind": "K" * 101, "value": "VALUE"}],
            },
        )

    assert response.status_code == 422
