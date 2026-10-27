"""Internal typing support for the stable public Python API."""

from __future__ import annotations

from typing import Protocol, TypeVar

_CommandT = TypeVar("_CommandT", contravariant=True)
_ResultT = TypeVar("_ResultT", covariant=True)


class Handler(Protocol[_CommandT, _ResultT]):
    """Minimal application-handler contract consumed by public capability APIs."""

    def handle(self, command: _CommandT, /) -> _ResultT:
        """Handle one application command or query."""
        ...
