"""Transaction boundary contracts exposed to the Application Layer."""

from __future__ import annotations

from types import TracebackType
from typing import Protocol, Self

from pysrmkit.ports.repositories.onboarding import SupplierOnboardingRepository
from pysrmkit.ports.repositories.relationship import SupplierRelationshipRepository


class SupplierOnboardingUnitOfWork(Protocol):
    """Atomic transaction boundary for starting Supplier onboarding."""

    @property
    def relationship_repository(self) -> SupplierRelationshipRepository: ...

    @property
    def onboarding_repository(self) -> SupplierOnboardingRepository: ...

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
