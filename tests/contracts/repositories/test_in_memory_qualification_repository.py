"""SupplierQualificationRepository contract execution for the in-memory adapter."""

from pysrmkit.adapters.memory.qualification_repository import (
    InMemorySupplierQualificationRepository,
)
from pysrmkit.ports.repositories.qualification import SupplierQualificationRepository
from tests.contracts.repositories.test_qualification_repository_contract import (
    SupplierQualificationRepositoryContract,
)


class TestInMemorySupplierQualificationRepository(SupplierQualificationRepositoryContract):
    def make_repository(self) -> SupplierQualificationRepository:
        return InMemorySupplierQualificationRepository()
