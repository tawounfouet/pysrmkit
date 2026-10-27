"""System clock adapter."""

from datetime import UTC, datetime


class SystemClock:
    """UTC clock backed by the host system time."""

    def now(self) -> datetime:
        return datetime.now(UTC)
