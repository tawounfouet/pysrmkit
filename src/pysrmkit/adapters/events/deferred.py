"""Deferred in-process Domain Event dispatch for explicit transaction boundaries."""

from __future__ import annotations

from pysrmkit.domain.common.events import DomainEvent
from pysrmkit.ports.events import DomainEventDispatcher


class DeferredDomainEventDispatcher:
    """Buffer events until the surrounding persistence transaction commits."""

    def __init__(self, downstream: DomainEventDispatcher) -> None:
        self._downstream = downstream
        self._pending: list[DomainEvent] = []

    def dispatch(self, events: tuple[DomainEvent, ...]) -> None:
        """Buffer events without publishing side effects yet."""

        self._pending.extend(events)

    def publish(self) -> None:
        """Publish all buffered events after a successful commit."""

        events = tuple(self._pending)
        if not events:
            return
        self._downstream.dispatch(events)
        self._pending.clear()

    def discard(self) -> None:
        """Discard buffered events when the surrounding transaction rolls back."""

        self._pending.clear()
