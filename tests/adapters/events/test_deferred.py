"""Tests for deferred Domain Event dispatch."""

from datetime import UTC, datetime

from pysrmkit.adapters.events.deferred import DeferredDomainEventDispatcher
from pysrmkit.domain.common.events import DomainEvent

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=UTC)


class SampleEvent(DomainEvent):
    """Minimal event used to exercise deferred dispatch."""


class RecordingDispatcher:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def dispatch(self, events: tuple[DomainEvent, ...]) -> None:
        self.events.extend(events)


def test_events_remain_buffered_until_publish() -> None:
    downstream = RecordingDispatcher()
    dispatcher = DeferredDomainEventDispatcher(downstream)
    event = SampleEvent(occurred_at=NOW)

    dispatcher.dispatch((event,))

    assert downstream.events == []

    dispatcher.publish()

    assert downstream.events == [event]


def test_discard_prevents_publication() -> None:
    downstream = RecordingDispatcher()
    dispatcher = DeferredDomainEventDispatcher(downstream)
    event = SampleEvent(occurred_at=NOW)

    dispatcher.dispatch((event,))
    dispatcher.discard()
    dispatcher.publish()

    assert downstream.events == []
