"""A3-06 observable Unicode search diagnostics for all three adapters.

These are characterization tests, not a promise of Unicode equivalence.
The exact ASCII contract is enforced separately by SupplierSearchContract.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from uuid import UUID

import pytest

from pysrmkit.adapters.memory.supplier_repository import InMemorySupplierRepository
from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.repositories.supplier import SqlAlchemySupplierRepository
from pysrmkit.adapters.sqlalchemy.schema import load_persistence_metadata
from pysrmkit.adapters.sqlalchemy.session import create_session_factory
from pysrmkit.domain.supplier.entities import Supplier
from pysrmkit.domain.supplier.value_objects import SupplierId, SupplierIdentity
from tests.contracts.queries.corpus import (
    UNICODE_PROBES,
    SearchableSupplierRepository,
    UnicodeProbe,
)


@pytest.fixture(
    params=[
        "memory",
        "sqlite",
        pytest.param("postgresql", marks=pytest.mark.postgresql),
    ]
)
def searchable_repository(
    request: pytest.FixtureRequest,
) -> Iterator[tuple[str, SearchableSupplierRepository]]:
    """Isolate one adapter for each Unicode probe, including real PostgreSQL."""
    backend = str(request.param)
    if backend == "memory":
        yield backend, InMemorySupplierRepository()
        return

    if backend == "postgresql":
        url = os.environ.get("PYSRMKIT_POSTGRESQL_TEST_URL")
        if url is None:
            pytest.skip("PYSRMKIT_POSTGRESQL_TEST_URL is not configured")
    else:
        url = "sqlite:///:memory:"

    engine = create_persistence_engine(url)
    metadata = load_persistence_metadata()
    if backend == "postgresql":
        metadata.drop_all(engine)
    metadata.create_all(engine)
    session = create_session_factory(engine)()
    try:
        yield backend, SqlAlchemySupplierRepository(session)
    finally:
        session.rollback()
        session.close()
        engine.dispose()


@pytest.mark.parametrize("probe", UNICODE_PROBES, ids=[probe.name for probe in UNICODE_PROBES])
def test_unicode_search_characterization(
    searchable_repository: tuple[str, SearchableSupplierRepository],
    probe: UnicodeProbe,
) -> None:
    """Record the provider result while asserting read-only query invariants."""
    backend, repository = searchable_repository
    identifier = SupplierId(UUID(int=1001))
    supplier = Supplier.reconstitute(
        supplier_id=identifier,
        identity=SupplierIdentity(legal_name=probe.legal_name),
    )
    repository.save(supplier)

    result = repository.search_suppliers(
        query=probe.query,
        country_code=None,
        supplier_type=None,
        sort_by="legal_name",
        sort_order="asc",
        offset=0,
        limit=100,
    )

    # Not a common Unicode oracle: every backend may legitimately differ
    # until an explicit storage, collation and normalization strategy exists.
    assert result.total in (0, 1)
    assert tuple(item.id for item in result.suppliers) in ((), (identifier,))
    assert len(result.suppliers) == result.total

    stored = repository.get(identifier)
    assert stored is not None
    assert stored.identity.legal_name == probe.legal_name
    assert repository.list_suppliers(offset=0, limit=100).total == 1
    assert stored.pull_events() == ()

    # Visible with pytest -s; the CI diagnostic steps retain the evidence.
    print(f"UNICODE_PROBE backend={backend} case={probe.name} matched={bool(result.total)}")
