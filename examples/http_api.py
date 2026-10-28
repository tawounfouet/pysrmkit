"""FastAPI host exposing the PySRMKit public Supplier capability."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.engine import Engine

from pysrmkit import PySRMKit
from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.public import ExternalIdentifierInput, SupplierView

DEFAULT_DATABASE_URL = "postgresql+psycopg://postgres@localhost:5432/pysrmkit"


class ExternalIdentifierPayload(BaseModel):
    kind: str = Field(min_length=1, max_length=100)
    value: str = Field(min_length=1, max_length=255)
    source_system: str | None = Field(default=None, max_length=100)
    jurisdiction_code: str | None = Field(default=None, min_length=2, max_length=2)


class SupplierCreatePayload(BaseModel):
    legal_name: str = Field(min_length=1, max_length=255)
    trading_name: str | None = Field(default=None, max_length=255)
    supplier_type: str | None = Field(default=None, max_length=100)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    external_identifiers: list[ExternalIdentifierPayload] = Field(
        default_factory=list,
        max_length=50,
    )


class ExternalIdentifierResponse(BaseModel):
    kind: str
    value: str
    source_system: str | None
    jurisdiction_code: str | None


class SupplierResponse(BaseModel):
    supplier_id: str
    legal_name: str
    trading_name: str | None
    supplier_type: str | None
    country_code: str | None
    external_identifiers: list[ExternalIdentifierResponse]


class SupplierPageResponse(BaseModel):
    items: list[SupplierResponse]
    total: int
    offset: int
    limit: int


class HealthResponse(BaseModel):
    status: str


def _supplier_response(supplier: SupplierView) -> SupplierResponse:
    return SupplierResponse(
        supplier_id=str(supplier.supplier_id),
        legal_name=supplier.legal_name,
        trading_name=supplier.trading_name,
        supplier_type=supplier.supplier_type,
        country_code=str(supplier.country) if supplier.country is not None else None,
        external_identifiers=[
            ExternalIdentifierResponse(
                kind=identifier.kind,
                value=identifier.value,
                source_system=identifier.source_system,
                jurisdiction_code=(
                    str(identifier.jurisdiction) if identifier.jurisdiction is not None else None
                ),
            )
            for identifier in supplier.external_identifiers
        ],
    )


def _matches_supplier(supplier: SupplierView, query: str) -> bool:
    searchable_values = (
        supplier.legal_name,
        supplier.trading_name,
        supplier.supplier_type,
        str(supplier.country) if supplier.country is not None else None,
        *(identifier.value for identifier in supplier.external_identifiers),
    )
    normalized_query = query.casefold()
    return any(
        normalized_query in value.casefold() for value in searchable_values if value is not None
    )


def _search_suppliers(srm: PySRMKit, query: str) -> list[SupplierView]:
    matches: list[SupplierView] = []
    source_offset = 0

    while True:
        page = srm.suppliers.list(offset=source_offset, limit=100)
        matches.extend(supplier for supplier in page.items if _matches_supplier(supplier, query))
        source_offset += len(page.items)
        if source_offset >= page.total or not page.items:
            return matches


def create_app(srm: PySRMKit, *, engine: Engine | None = None) -> FastAPI:
    """Create an HTTP host around an already composed PySRMKit runtime."""

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        if engine is not None:
            engine.dispose()

    app = FastAPI(
        title="PySRMKit Supplier API",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        srm.suppliers.list(limit=1)
        return HealthResponse(status="ok")

    @app.get("/suppliers", response_model=SupplierPageResponse)
    def list_suppliers(
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 25,
        query: Annotated[str | None, Query(max_length=100)] = None,
    ) -> SupplierPageResponse:
        if query and query.strip():
            matches = _search_suppliers(srm, query.strip())
            return SupplierPageResponse(
                items=[
                    _supplier_response(supplier) for supplier in matches[offset : offset + limit]
                ],
                total=len(matches),
                offset=offset,
                limit=limit,
            )

        page = srm.suppliers.list(offset=offset, limit=limit)
        return SupplierPageResponse(
            items=[_supplier_response(supplier) for supplier in page.items],
            total=page.total,
            offset=page.offset,
            limit=page.limit,
        )

    @app.post(
        "/suppliers",
        response_model=SupplierResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def create_supplier(payload: SupplierCreatePayload) -> SupplierResponse:
        try:
            result = srm.suppliers.register(
                legal_name=payload.legal_name,
                trading_name=payload.trading_name,
                supplier_type=payload.supplier_type,
                country_code=payload.country_code,
                external_identifiers=tuple(
                    ExternalIdentifierInput(
                        kind=identifier.kind,
                        value=identifier.value,
                        source_system=identifier.source_system,
                        jurisdiction_code=identifier.jurisdiction_code,
                    )
                    for identifier in payload.external_identifiers
                ),
            )
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

        supplier = srm.suppliers.get(supplier_id=result.supplier_id)
        return _supplier_response(supplier)

    return app


database_url = os.getenv("PYSRMKIT_DATABASE_URL", DEFAULT_DATABASE_URL)
database_engine = create_persistence_engine(database_url)
app = create_app(PySRMKit.sql(database_engine), engine=database_engine)
