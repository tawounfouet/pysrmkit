"""SQLAlchemy-to-public error translation for the SQL runtime."""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

from pysrmkit.public._handler import Handler
from pysrmkit.public.errors import (
    PersistenceConflict,
    PersistenceError,
    PersistenceUnavailable,
)

_CommandT = TypeVar("_CommandT")
_ResultT = TypeVar("_ResultT")


class SqlAlchemyErrorBoundaryHandler(Generic[_CommandT, _ResultT]):
    """Translate SQLAlchemy failures without changing business errors."""

    def __init__(self, handler: Handler[_CommandT, _ResultT]) -> None:
        self._handler = handler

    def handle(self, command: _CommandT, /) -> _ResultT:
        try:
            return self._handler.handle(command)
        except IntegrityError as exc:
            raise PersistenceConflict("Persistence constraint conflict") from exc
        except OperationalError as exc:
            raise PersistenceUnavailable("Persistence backend is unavailable") from exc
        except SQLAlchemyError as exc:
            raise PersistenceError("Persistence operation failed") from exc
