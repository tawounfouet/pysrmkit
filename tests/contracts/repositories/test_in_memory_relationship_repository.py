"""SupplierRelationshipRepository contract execution for the in-memory adapter."""

from pysrmkit.adapters.memory.relationship_repository import (
    InMemorySupplierRelationshipRepository,
)
from pysrmkit.ports.repositories.relationship import SupplierRelationshipRepository
from tests.contracts.repositories.test_relationship_repository_contract import (
    SupplierRelationshipRepositoryContract,
)


class TestInMemorySupplierRelationshipRepository(SupplierRelationshipRepositoryContract):
    def make_repository(self) -> SupplierRelationshipRepository:
        return InMemorySupplierRelationshipRepository()
