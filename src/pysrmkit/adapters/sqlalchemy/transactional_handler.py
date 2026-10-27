"""Transactional handler adapter for SQLAlchemy-backed public runtimes."""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from pysrmkit.public._handler import Handler

_CommandT = TypeVar("_CommandT")
_ResultT = TypeVar("_ResultT")


class SqlAlchemyTransactionalHandler(Generic[_CommandT, _ResultT]):
    """Execute one application handler invocation in one SQL transaction.

    This adapter keeps SQLAlchemy Session lifetime and commit/rollback semantics
    outside the Application Layer. A fresh Session is created for every public
    operation, making the transaction boundary explicit without a global Session.
    """

    def __init__(
        self,
        *,
        session_factory: Callable[[], Session],
        handler_factory: Callable[[Session], Handler[_CommandT, _ResultT]],
    ) -> None:
        self._session_factory = session_factory
        self._handler_factory = handler_factory

    def handle(self, command: _CommandT, /) -> _ResultT:
        with self._session_factory() as session:
            with session.begin():
                handler = self._handler_factory(session)
                return handler.handle(command)
