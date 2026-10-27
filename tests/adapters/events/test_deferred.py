"""Tests for deferred Domain Event dispatch."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from pysrmkit.adapters.events.deferred import DeferredDomainEventDispatcher
from pysrmkit.domain.common.events import DomainEvent

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class SampleEvent:
    """Minimal structural implementation of the DomainEvent Protocol."""

    occurred_at: datetime
    event_id: UUID


class RecordingDispatcher:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def dispatch(self, events: tuple[DomainEvent, ...]) -> None:
        self.events.extend(events)


def test_events_remain_buffered_until_publish() -> None:
    downstream = RecordingDispatcher()
    dispatcher = DeferredDomainEventDispatcher(downstream)
    event = SampleEvent(occurred_at=NOW, event_id=uuid4())

    dispatcher.dispatch((event,))

    assert downstream.events == []

    dispatcher.publish()

    assert downstream.events == [event]


def test_discard_prevents_publication() -> None:
    downstream = RecordingDispatcher()
    dispatcher = DeferredDomainEventDispatcher(downstream)
    event = SampleEvent(occurred_at=NOW, event_id=uuid4())

    dispatcher.dispatch((event,))
    dispatcher.discard()
    dispatcher.publish()

    assert downstream.events == []
