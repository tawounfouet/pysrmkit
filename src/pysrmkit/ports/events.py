"""Domain-event dispatch port."""

from __future__ import annotations

from typing import Protocol

from pysrmkit.domain.common.events import DomainEvent


class DomainEventDispatcher(Protocol):
    """Publishes Domain Events recorded during an application use case."""

    def dispatch(self, events: tuple[DomainEvent, ...]) -> None: ...
