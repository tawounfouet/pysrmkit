"""Minimal domain-event contract for PySRMKit."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID


class DomainEvent(Protocol):
    """Significant immutable business fact recorded by an Aggregate."""

    @property
    def event_id(self) -> UUID: ...

    @property
    def occurred_at(self) -> datetime: ...
