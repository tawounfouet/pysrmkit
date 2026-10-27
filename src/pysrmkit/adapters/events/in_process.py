"""Synchronous in-process implementation of DomainEventDispatcher."""

from __future__ import annotations

from collections.abc import Callable

from pysrmkit.domain.common.events import DomainEvent

DomainEventHandler = Callable[[DomainEvent], None]


class InProcessDomainEventDispatcher:
    """Dispatches Domain Events synchronously to handlers registered by exact type."""

    def __init__(self) -> None:
        self._handlers: dict[type[object], list[DomainEventHandler]] = {}

    def register(self, event_type: type[object], handler: DomainEventHandler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def dispatch(self, events: tuple[DomainEvent, ...]) -> None:
        for event in events:
            for handler in self._handlers.get(type(event), []):
                handler(event)
