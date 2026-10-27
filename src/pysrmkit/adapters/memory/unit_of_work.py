"""Transactional in-memory UnitOfWork for Supplier onboarding."""

from __future__ import annotations

from types import TracebackType
from typing import Self

from pysrmkit.adapters.memory.onboarding_repository import (
    InMemorySupplierOnboardingRepository,
    _StoredOnboarding,
)
from pysrmkit.adapters.memory.relationship_repository import (
    InMemorySupplierRelationshipRepository,
    _StoredRelationship,
)
from pysrmkit.domain.onboarding.value_objects import OnboardingId
from pysrmkit.domain.relationship.value_objects import SupplierRelationshipId
from pysrmkit.ports.repositories.onboarding import SupplierOnboardingRepository
from pysrmkit.ports.repositories.relationship import SupplierRelationshipRepository


class InMemorySupplierOnboardingUnitOfWork:
    """Atomic snapshot/restore boundary across Relationship and Onboarding stores."""

    def __init__(
        self,
        *,
        relationship_repository: InMemorySupplierRelationshipRepository,
        onboarding_repository: InMemorySupplierOnboardingRepository,
    ) -> None:
        self._relationship_repository = relationship_repository
        self._onboarding_repository = onboarding_repository
        self._relationship_snapshot: (
            dict[SupplierRelationshipId, _StoredRelationship] | None
        ) = None
        self._onboarding_snapshot: dict[OnboardingId, _StoredOnboarding] | None = None
        self._committed = False

    @property
    def relationship_repository(self) -> SupplierRelationshipRepository:
        return self._relationship_repository

    @property
    def onboarding_repository(self) -> SupplierOnboardingRepository:
        return self._onboarding_repository

    def __enter__(self) -> Self:
        if self._relationship_snapshot is not None or self._onboarding_snapshot is not None:
            raise RuntimeError("UnitOfWork is already active")
        self._relationship_snapshot = self._relationship_repository._snapshot_state()
        self._onboarding_snapshot = self._onboarding_repository._snapshot_state()
        self._committed = False
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None or not self._committed:
            self.rollback()
        self._relationship_snapshot = None
        self._onboarding_snapshot = None
        self._committed = False

    def commit(self) -> None:
        self._require_active()
        self._committed = True

    def rollback(self) -> None:
        self._require_active()
        self._relationship_repository._restore_state(self._relationship_snapshot)
        self._onboarding_repository._restore_state(self._onboarding_snapshot)
        self._committed = False

    def _require_active(self) -> None:
        if self._relationship_snapshot is None or self._onboarding_snapshot is None:
            raise RuntimeError("UnitOfWork is not active")
