"""SupplierOnboardingRepository contract execution for the in-memory adapter."""

from pysrmkit.adapters.memory.onboarding_repository import InMemorySupplierOnboardingRepository
from pysrmkit.ports.repositories.onboarding import SupplierOnboardingRepository
from tests.contracts.repositories.test_onboarding_repository_contract import (
    SupplierOnboardingRepositoryContract,
)


class TestInMemorySupplierOnboardingRepository(SupplierOnboardingRepositoryContract):
    def make_repository(self) -> SupplierOnboardingRepository:
        return InMemorySupplierOnboardingRepository()
