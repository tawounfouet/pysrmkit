"""A3-01 shared Supplier search contract for deterministic ASCII cases.

The same abstract test suite executes against the InMemory and SQLite
implementations. A3-05 adds a real PostgreSQL implementor without rewriting
any expected results or adapter-specific test logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pytest

from pysrmkit.adapters.memory.supplier_repository import InMemorySupplierRepository
from pysrmkit.adapters.sqlalchemy.engine import create_persistence_engine
from pysrmkit.adapters.sqlalchemy.repositories.supplier import SqlAlchemySupplierRepository
from pysrmkit.adapters.sqlalchemy.schema import load_persistence_metadata
from pysrmkit.adapters.sqlalchemy.session import create_session_factory
from pysrmkit.domain.supplier.value_objects import CountryCode
from tests.contracts.queries.corpus import (
    ASCII_SUPPLIERS,
    SEARCH_CASES,
    SearchableSupplierRepository,
    SearchCase,
    expected_supplier_ids,
    seed_ascii_corpus,
)


class SupplierSearchContract(ABC):
    """Shared behavioral specification, independent from adapter technology.

    Design: Contract Testing + LSP + DIP; an adapter supplies only a factory.
    """

    @abstractmethod
    def make_repository(self) -> SearchableSupplierRepository:
        raise NotImplementedError

    @pytest.mark.parametrize("case", SEARCH_CASES, ids=[case.name for case in SEARCH_CASES])
    def test_search_matches_expected_corpus(self, case: SearchCase) -> None:
        repository = self.make_repository()
        seed_ascii_corpus(repository)

        result = repository.search_suppliers(
            query=case.query,
            country_code=CountryCode(case.country_code)
            if case.country_code is not None
            else None,
            supplier_type=case.supplier_type,
            sort_by="legal_name",
            sort_order=case.sort_order,
            offset=case.offset,
            limit=case.limit,
        )

        assert result.total == case.total, case.name
        assert tuple(supplier.id for supplier in result.suppliers) == expected_supplier_ids(
            case
        ), case.name
        assert len(result.suppliers) <= case.limit

    def test_search_retains_canonical_identity_and_identifier(self) -> None:
        repository = self.make_repository()
        seed_ascii_corpus(repository)

        page = repository.search_suppliers(
            query="Atlas Components",
            country_code=CountryCode("FR"),
            supplier_type="MANUFACTURER",
            sort_by="legal_name",
            sort_order="asc",
            offset=0,
            limit=100,
        )

        assert page.total == 2
        for supplier in page.suppliers:
            original = repository.get(supplier.id)
            assert original is not None
            assert supplier.identity == original.identity
            assert supplier.external_identifiers == original.external_identifiers
            assert supplier.pull_events() == ()

    def test_search_preserves_existing_uuid_ordered_listing(self) -> None:
        repository = self.make_repository()
        seed_ascii_corpus(repository)

        before = repository.list_suppliers(offset=0, limit=100)
        repository.search_suppliers(
            query="Atlas",
            country_code=None,
            supplier_type=None,
            sort_by="legal_name",
            sort_order="desc",
            offset=0,
            limit=2,
        )
        after = repository.list_suppliers(offset=0, limit=100)

        assert before.total == after.total == len(ASCII_SUPPLIERS)
        assert tuple(supplier.id for supplier in before.suppliers) == tuple(
            entry.supplier_id for entry in ASCII_SUPPLIERS
        )
        assert tuple(supplier.id for supplier in before.suppliers) == tuple(
            supplier.id for supplier in after.suppliers
        )


class TestInMemorySupplierSearchContract(SupplierSearchContract):
    repository: InMemorySupplierRepository

    def setup_method(self) -> None:
        self.repository = InMemorySupplierRepository()

    def make_repository(self) -> SearchableSupplierRepository:
        return self.repository


class TestSqliteSupplierSearchContract(SupplierSearchContract):
    repository: SqlAlchemySupplierRepository

    def setup_method(self) -> None:
        self.engine = create_persistence_engine("sqlite:///:memory:")
        load_persistence_metadata().create_all(self.engine)
        self.session = create_session_factory(self.engine)()
        self.repository = SqlAlchemySupplierRepository(self.session)

    def teardown_method(self) -> None:
        self.session.rollback()
        self.session.close()
        self.engine.dispose()

    def make_repository(self) -> SearchableSupplierRepository:
        return self.repository


def test_corpus_has_unique_codes_and_stable_supplier_ids() -> None:
    codes = tuple(item.code for item in ASCII_SUPPLIERS)
    ids = tuple(item.supplier_id for item in ASCII_SUPPLIERS)

    assert len(codes) == len(set(codes)) == 13
    assert len(ids) == len(set(ids)) == 13
    assert ids == tuple(sorted(ids, key=lambda supplier_id: supplier_id.value))
    assert all(set(case.expected_codes).issubset(codes) for case in SEARCH_CASES)


def test_corpus_cases_have_consistent_declared_totals() -> None:
    """A paged result must not claim fewer matches than its visible page."""
    assert all(case.total >= len(case.expected_codes) for case in SEARCH_CASES)
    assert all(len(case.expected_codes) <= case.limit for case in SEARCH_CASES)
