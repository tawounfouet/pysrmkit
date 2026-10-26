"""System clock adapter."""

from datetime import datetime, timezone


class SystemClock:
    """UTC clock backed by the host system time."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)
