"""Clock port used by application use cases that need current time."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Provides time without coupling application code to the system clock."""

    def now(self) -> datetime: ...
