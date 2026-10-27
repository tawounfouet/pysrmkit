"""SQLAlchemy UnitOfWork for the Supplier onboarding transaction."""

from __future__ import annotations

from collections.abc import Callable
from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session

from pysrmkit.adapters.sqlalchemy.repositories.onboarding import (
    SqlAlchemySupplierOnboardingRepository,
)
from pysrmkit.adapters.sqlalchemy.repositories.relationship import (
    SqlAlchemySupplierRelationshipRepository,
)
from pysrmkit.ports.repositories.onboarding import SupplierOnboardingRepository
from pysrmkit.ports.repositories.relationship import SupplierRelationshipRepository


class SqlAlchemySupplierOnboardingUnitOfWork:
    """Own one SQLAlchemy Session shared by both participating repositories."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self._relationship_repository: SqlAlchemySupplierRelationshipRepository | None = None
        self._onboarding_repository: SqlAlchemySupplierOnboardingRepository | None = None
        self._committed = False

    @property
    def relationship_repository(self) -> SupplierRelationshipRepository:
        if self._relationship_repository is None:
            raise RuntimeError("UnitOfWork is not active")
        return self._relationship_repository

    @property
    def onboarding_repository(self) -> SupplierOnboardingRepository:
        if self._onboarding_repository is None:
            raise RuntimeError("UnitOfWork is not active")
        return self._onboarding_repository

    def __enter__(self) -> Self:
        if self._session is not None:
            raise RuntimeError("UnitOfWork is already active")
        session = self._session_factory()
        self._session = session
        self._relationship_repository = SqlAlchemySupplierRelationshipRepository(session)
        self._onboarding_repository = SqlAlchemySupplierOnboardingRepository(session)
        self._committed = False
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        session = self._session
        if session is None:
            return
        try:
            if exc_type is not None or not self._committed:
                session.rollback()
        finally:
            session.close()
            self._session = None
            self._relationship_repository = None
            self._onboarding_repository = None
            self._committed = False

    def commit(self) -> None:
        session = self._require_session()
        session.commit()
        self._committed = True

    def rollback(self) -> None:
        session = self._require_session()
        session.rollback()
        self._committed = False

    def _require_session(self) -> Session:
        if self._session is None:
            raise RuntimeError("UnitOfWork is not active")
        return self._session
