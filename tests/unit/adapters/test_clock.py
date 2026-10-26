"""Clock adapter tests."""

from datetime import datetime, timezone

from pysrmkit.adapters.clock.fixed import FixedClock
from pysrmkit.adapters.clock.system import SystemClock
from pysrmkit.ports.clock import Clock


def test_fixed_clock_returns_configured_instant() -> None:
    instant = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)
    clock: Clock = FixedClock(instant)

    assert clock.now() == instant


def test_system_clock_returns_timezone_aware_utc_time() -> None:
    clock: Clock = SystemClock()

    current = clock.now()

    assert current.tzinfo is timezone.utc
