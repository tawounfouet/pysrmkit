"""SupplierAssessmentRepository contract execution for the in-memory adapter."""

from pysrmkit.adapters.memory.assessment_repository import InMemorySupplierAssessmentRepository
from pysrmkit.ports.repositories.assessment import SupplierAssessmentRepository
from tests.contracts.repositories.test_assessment_repository_contract import (
    SupplierAssessmentRepositoryContract,
)


class TestInMemorySupplierAssessmentRepository(SupplierAssessmentRepositoryContract):
    def make_repository(self) -> SupplierAssessmentRepository:
        return InMemorySupplierAssessmentRepository()
