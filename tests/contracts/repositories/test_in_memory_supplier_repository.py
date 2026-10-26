"""SupplierRepository contract execution for the in-memory adapter."""

from pysrmkit.adapters.memory.supplier_repository import InMemorySupplierRepository
from pysrmkit.ports.repositories.supplier import SupplierRepository
from tests.contracts.repositories.test_supplier_repository_contract import (
    SupplierRepositoryContract,
    make_supplier,
)


class TestInMemorySupplierRepository(SupplierRepositoryContract):
    def make_repository(self) -> SupplierRepository:
        return InMemorySupplierRepository()


def test_in_memory_repository_does_not_persist_pending_domain_events() -> None:
    repository = InMemorySupplierRepository()
    supplier = make_supplier()
    assert supplier.pull_events()

    repository.save(supplier)
    loaded = repository.get(supplier.id)

    assert loaded is not None
    assert loaded.pull_events() == ()
