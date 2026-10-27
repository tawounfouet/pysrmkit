"""Deterministic clock adapter for local execution and tests."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class FixedClock:
    """Clock that always returns the same instant."""

    instant: datetime

    def now(self) -> datetime:
        return self.instant
