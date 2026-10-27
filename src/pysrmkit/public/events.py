"""Typed public in-process Domain Event subscription surface."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from pysrmkit.adapters.events.in_process import InProcessDomainEventDispatcher

_EventT = TypeVar("_EventT")


class EventsAPI:
    """Subscribe synchronously to selected public Domain Events.

    Delivery is in-process and non-durable. Handlers run after the business operation
    has reached its publication point. SQL runtimes publish only after a successful
    database commit. No at-least-once, exactly-once, replay, or crash-recovery
    guarantee is provided.
    """

    def __init__(self, dispatcher: InProcessDomainEventDispatcher) -> None:
        self._dispatcher = dispatcher

    def subscribe(
        self,
        event_type: type[_EventT],
        handler: Callable[[_EventT], None],
    ) -> None:
        """Register a synchronous handler for one exact public event type."""

        def dispatch(event: object) -> None:
            if isinstance(event, event_type):
                handler(event)

        self._dispatcher.register(event_type, dispatch)
