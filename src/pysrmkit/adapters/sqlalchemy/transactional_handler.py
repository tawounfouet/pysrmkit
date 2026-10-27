"""Transactional handler adapter for SQLAlchemy-backed public runtimes."""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from pysrmkit.adapters.events.deferred import DeferredDomainEventDispatcher
from pysrmkit.ports.events import DomainEventDispatcher
from pysrmkit.public._handler import Handler

_CommandT = TypeVar("_CommandT")
_ResultT = TypeVar("_ResultT")


class SqlAlchemyTransactionalHandler(Generic[_CommandT, _ResultT]):
    """Execute one application handler invocation in one SQL transaction.

    A fresh Session is created for every public operation. When an event-aware
    handler factory is supplied, Domain Events are buffered during the transaction,
    published only after commit, and discarded after rollback/failure.
    """

    def __init__(
        self,
        *,
        session_factory: Callable[[], Session],
        handler_factory: Callable[[Session], Handler[_CommandT, _ResultT]] | None = None,
        event_dispatcher: DomainEventDispatcher | None = None,
        event_handler_factory: Callable[
            [Session, DomainEventDispatcher],
            Handler[_CommandT, _ResultT],
        ]
        | None = None,
    ) -> None:
        if (handler_factory is None) == (event_handler_factory is None):
            raise ValueError("Provide exactly one handler factory")
        if event_handler_factory is not None and event_dispatcher is None:
            raise ValueError("event_dispatcher is required for an event-aware handler factory")
        self._session_factory = session_factory
        self._handler_factory = handler_factory
        self._event_dispatcher = event_dispatcher
        self._event_handler_factory = event_handler_factory

    def handle(self, command: _CommandT, /) -> _ResultT:
        deferred = (
            DeferredDomainEventDispatcher(self._event_dispatcher)
            if self._event_dispatcher is not None
            else None
        )
        try:
            with self._session_factory() as session:
                with session.begin():
                    handler = self._make_handler(session, deferred)
                    result = handler.handle(command)
            if deferred is not None:
                deferred.publish()
            return result
        except BaseException:
            if deferred is not None:
                deferred.discard()
            raise

    def _make_handler(
        self,
        session: Session,
        deferred: DeferredDomainEventDispatcher | None,
    ) -> Handler[_CommandT, _ResultT]:
        if self._event_handler_factory is not None:
            if deferred is None:
                raise RuntimeError("Deferred event dispatcher is unavailable")
            return self._event_handler_factory(session, deferred)
        if self._handler_factory is None:
            raise RuntimeError("Handler factory is unavailable")
        return self._handler_factory(session)
