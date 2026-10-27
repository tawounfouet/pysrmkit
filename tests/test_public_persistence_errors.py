"""Tests for SQL persistence error translation at the public boundary."""

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

from pysrmkit.public._sql_boundary import SqlAlchemyErrorBoundaryHandler
from pysrmkit.public.errors import (
    PersistenceConflict,
    PersistenceError,
    PersistenceUnavailable,
)


class FailingHandler:
    def __init__(self, error: Exception) -> None:
        self._error = error

    def handle(self, command: object, /) -> None:
        del command
        raise self._error


def test_integrity_error_becomes_persistence_conflict() -> None:
    handler = SqlAlchemyErrorBoundaryHandler[object, None](
        FailingHandler(IntegrityError("statement", {}, Exception("constraint")))
    )

    with pytest.raises(PersistenceConflict):
        handler.handle(object())


def test_operational_error_becomes_persistence_unavailable() -> None:
    handler = SqlAlchemyErrorBoundaryHandler[object, None](
        FailingHandler(OperationalError("statement", {}, Exception("offline")))
    )

    with pytest.raises(PersistenceUnavailable):
        handler.handle(object())


def test_other_sqlalchemy_error_becomes_persistence_error() -> None:
    handler = SqlAlchemyErrorBoundaryHandler[object, None](
        FailingHandler(SQLAlchemyError("storage failure"))
    )

    with pytest.raises(PersistenceError):
        handler.handle(object())
